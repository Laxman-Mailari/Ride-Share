import os
from flask import Flask, jsonify, request,\
abort, Response,  redirect, url_for
from flask_pymongo import PyMongo
from pymongo import MongoClient
from datetime import datetime
from bson import Binary, Code
from bson.json_util import dumps, loads
import json
import hashlib
import requests
import datetime
import re

from functools import wraps

app = Flask(__name__)
#app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
#mongo = PyMongo(app)
#db = mongo.db


@app.route('/api/v1/users',methods=['POST','PATCH','DELETE','COPY','HEAD','OPTIONS','LINK','UNLINK','PURGE','LOCK','UNLOCK','PROPFIND','VIEW'])
def unuser():
   return jsonify({}),405
   
   
@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    req_data = request.get_json()

    name = req_data['username']
    passw = req_data['password']
    if(name == "" or passw == ""):
        return jsonify({}), 400

    hash_pass = hashlib.sha1(passw.encode())
    #print(hash_pass.hexdigest(),'-----------' ,hash_pass)
    query = {'collection': 'users','data':{ 'username': name}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    if(len(rdata) > 0):
        #return "Take diff username"
        return jsonify({}),400

    query = {'collection': 'users','work': 'insert', 'data': {'username': name, 'password': hash_pass.hexdigest()}}
    a = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)
    #print(a.status_code, a.reason,a.text)
    return jsonify({}),201

@app.route('/api/v1/users/<string:user>', methods=['GET','POST','PATCH','PUT','COPY','HEAD','OPTIONS','LINK','UNLINK','PURGE','LOCK','UNLOCK','PROPFIND','VIEW'])
def no_user():
    return jsonify({}),405


@app.route('/api/v1/users/<string:user>', methods=['DELETE'])
def delete_user(user):
    query = {'collection': 'users','data':{ 'username': user}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    if(len(rdata) > 0):
        query = {'collection': 'rides','data':{ 'created_by': user}}
        rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
        rdata = loads(rec.text)
        
        if(len(rdata) > 0):
            query = {'collection': 'rides','work': 'delete', 'data':{ 'created_by': user}}
            rec = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)

        #data = db.users.find({"username": user})
        query = {'collection': 'users','work': 'delete','data':{ 'username': user}}
        a = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)
        return jsonify({}),200

    else:
        return jsonify({}),400


'''
@app.route('/api/v1/db/write', methods=['POST'])
def write():
    req_data = request.get_json()
    collection = req_data['collection']
    data = req_data['data']

    if(req_data['work'] == 'insert'):
        db[collection].insert(data)
        return jsonify({}), 201

    if(req_data['work'] == 'delete'):
        db[collection].remove(data)
        return jsonify({}), 201

    if(req_data['work'] == 'update'):
        data = req_data['data']
        #print("updatea here --- ",data[0],data[1])
        #db[collection].update(data[0],data[1])
        b = db[collection].update({"name":"counter"},{'$set':{"count":data[1]}})
        return jsonify({}), 201



@app.route('/api/v1/db/read', methods=['POST'])
def read():
    req_data = request.get_json()
    collection = req_data['collection']
    data = req_data['data']
    if(data == 'distinct'):
        data1 =  req_data['value']
        send_data = db[collection].distinct(data1)
        return dumps(send_data), 200

    send_data = db[collection].find(data)
    return dumps(send_data), 200

'''

@app.route('/api/v1/users', methods=['GET'])
def list_all_users():
    query = {'collection': 'users','data':'distinct','value': 'username'}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text)
    if(len(rdata) > 0):
        return json.dumps(rdata), 200
    else:
        return json.dumps(rdata), 204

'''
@app.route('/api/v1/db/clear', methods=['POST'])
def clear_db():
    db.users.remove({})
    db.rides.remove({})
    return jsonify({}), 200

@app.route('/api/v1/_count',methods=['GET'])
def http_request():
   COUNT=read_count()
   #count = json.loads(COUNT)
   #COUNT = int(COUNT_1[1])
   return dumps([COUNT]),200

@app.route('/api/v1/_count',methods=['DELETE'])
def delete_count():
   #rdata = 0
   #query = {'collection': 'count_http','work': 'update', 'data': {'count':rdata}}
   #a = requests.post(url='http://35.168.216.32:80/api/v1/db/write',json=query)
   b = db["count_http"].update({"name":"counter"},{'$set':{"count":0}})
   return jsonify({}),200
'''
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"MyError" : "method not allowed"}),405

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"MyError" : "Page not found"}),404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"MyError" : "Server Error"}),500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
   

