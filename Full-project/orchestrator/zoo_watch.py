from kazoo.client import KazooClient
import logging
#from dbaas.orchestrator.config import client, apiClient
import time
import sys
import random
import string
import socket
from kazoo.client import KazooState

def bring_up_new_worker_container(slave_name, db_name):
    print("[+] Starting(A) container: " + db_name, file=sys.stdout)

    client.containers.run(
        image='mongo:4.0',
        detach=True,
        name=db_name,
        environment={"MONGO_INITDB_ROOT_USERNAME":"admin","MONGO_INITDB_ROOT_PASSWORD":"password","MONGO_INITDB_DATABASE":"mymongodb"},
        network="zubairapp_default",
        volumes={'/home/ubuntu/flaskapp/mongo-init.js': {'bind': '/docker-entrypoint-initdb.d/mongo-init.js', 'mode': 'ro'}},
        remove=False
    )
    time.sleep(5)

    print("[+] Starting(A) container: " + slave_name, file=sys.stdout)
    img=client.images.build(path=".",dockerfile="Dockerfile")
    client.containers.run(
        img[0].id,
        command=["sh","-c","sleep 15 && python slv.py"],
        detach=True,
        name=slave_name,
        network="zubairapp_default",
        environment={"type":"slave","MONGODB_DATABASE":"mymongodb","MONGODB_USERNAME":"admin","MONGODB_PASSWORD": "password","MONGODB_HOSTNAME":db_name},
        links={"rmq":slave_name,db_name:slave_name,"zoo":slave_name},
        remove=False
    )


def listdiff(l1, l2):
    if len(l1) > len(l2):
        for i in l1:
            if i not in l2:
                return i
    else:
        for i in l2:
            if i not in l1:
                return i


class ZooWatch:
    def __init__(self):
        print("Zoo watch init")
        logging.basicConfig()
        self.zk = KazooClient(hosts='zoo:2181')
        self.zk.start()
        self.temp = []
        self.master_db_name = "mongomaster"

    def start(self):
        print("[*] Starting zoo watch", file=sys.stdout)
        self.zk.ensure_path("/worker")

        @self.zk.ChildrenWatch("/worker")
        def callback_worker(workers):
            print("[*] Changes detected", file=sys.stdout)
            print(workers, self.temp)
            if len(workers) < len(self.temp):
                node = listdiff(self.temp, workers)
                print("[-] Node deleted: " + node, file=sys.stdout)
                print("[*] Current workers: " + str(workers), file=sys.stdout)
                if "slv" in node:
                    killed_containers = client.containers.list(all=True, filters={"exited": "137"})
                    slave_cnt = client.containers.get(node)
                    i = slave_cnt.name[-1]
                    slave_db_cnt = client.containers.get("mongodb" + i)
                    if slave_cnt in killed_containers:
                        slave_cnt.remove()
                        slave_db_cnt.remove()
                        random_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
                        bring_up_new_worker_container(
                            slave_name="slv" + random_name,
                            db_name="mongodb" + random_name
                        )
                    else:
                        print("[*] Scaling down - removing " + node)
                        print("[*] Or newly elected master is deleting its old node")
                else:
                    print("[-] Master failed", file=sys.stdout)
                    

            elif len(workers) > len(self.temp):
                print("[+] Node added: " + listdiff(self.temp, workers), file=sys.stdout)
                print("[*] Current workers: " + str(workers), file=sys.stdout)

            else:
                pass

            self.temp = workers

        while True:
            pass

