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



def get_timestamp(timestamp):
    date,time = timestamp.split(':')
    dd,mm,yy = date.split('-')
    ss,min,hh = time.split('-')

    isValidDate = True

    try:
        datetime.datetime(int(yy),int(mm),int(dd))
    except ValueError:
        isValidDate = False
    if(isValidDate):
        if(int(ss) > 59 or int(min) > 59 or int(hh) > 23):
            return "not-valid"
        else:
            return "valid"
    else:
        return "not-valid"


@app.route('/api/v1/rides/hello',methods=['GET'])
def test_hello():
   # print("called test ")
    return "hello riders",200

@app.route('/api/v1/rides', methods=['PUT','PATCH','DELETE','COPY','HEAD','OPTIONS','LINK','UNLINK','PURGE','LOCK','UNLOCK','PROPFIND','VIEW'])
def no_rider():
    return jsonify({}),405


@app.route('/api/v1/rides', methods=['POST'])
def create_ride():
    req_data = request.get_json()
    name = req_data['created_by']
    print("over------------------------------->")
    
    #data = db.users.find({'username': name})
    #query = {'collection': 'users','data':{ 'username': name}}
    #query = {'collection': 'users','data':'distinct','value': 'username'}
    #rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
  
    rec = requests.get(url='http://Load-Manager-2051881000.us-east-1.elb.amazonaws.com/api/v1/users',headers= {'Origin': '52.55.216.208'})
    print("over------------------------------->")
    rdata_old = loads(rec.text)
    print("over------------------------------->")
    rdata = []
    for val in rdata_old:
        if (name == val):
            rdata.append(val)
    '''
    query = {'collection': 'users','data':'distinct','value': 'username'}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text)
    '''
    rideId = 1
    max = 0

    if(len(rdata) > 0):
        timestamp = req_data['timestamp']
        # query = {'timestamp': timestamp}
        # rec = requests.post(url='http://assg3-lb-1719997549.us-east-1.elb.amazonaws.com/api/time',json=query)
        tm = get_timestamp(timestamp)
        if(tm != "valid"):
            return jsonify({}), 400


        #rides = list(db.rides.find())
        query = {'collection': 'rides','data':{}}
        rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
        rides = loads(rec.text)

        if(len(rides) <= 0):
            rideId = 1
        else:
            
            for i in range(0,len(rides)):
                
                if(rides[i]['rideId'] > max):
                    max = rides[i]['rideId']
                    rideId = max+1


        source = req_data['source']
        if(int(source) < 1 or int(source) > 198):
            return jsonify({}), 400

        dest = req_data['destination']
        if(int(dest) < 1 or int(dest) > 198):
            return jsonify({}), 400
        # db.rides.insert({
            # 'rideId': rideId,
            # 'created_by': name,
            # 'joinee': [],
            # 'timestamp' : timestamp,
            # 'source':source,
            # 'destination': dest
        # })
        query = {'collection': 'rides','work': 'insert', 'data': {'rideId': rideId,'created_by': name,'users': [],
            'timestamp' : timestamp,'source':source,'destination': dest}}
        a = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)
        return jsonify({}),201

    else:
        return jsonify({}),400




@app.route('/api/v1/rides', methods=['GET'])
def upcoming_rides():
    #increment()
    if('source' in request.args):
       	source = request.args['source']
    else:
        return jsonify({}), 400
       # return "it is  not  found",200

    if('destination' in request.args):
        destination = request.args['destination']
    else:
        return jsonify({}), 400


    if(int(source) < 1 or int(source) > 198):
        return jsonify({}), 400

    if(int(destination) < 1 or int(destination) > 198):
        return jsonify({}), 400

    #data = list(db.rides.find({'source':source , 'destination':destination}))
    query = {'collection': 'rides','data':{'source':source , 'destination':destination}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
    #print(rdata)

    rides_list = []
    if(len(rdata) > 0):
        j=len(rdata)
        for i in range(0,j):
            rides_list.append(  {"rideId" : rdata[i]['rideId'],
            "username" : rdata[i]['created_by'] ,
            "timestamp" : rdata[i]['timestamp']
            })

        return json.dumps(rides_list),200
    else:
        return json.dumps(rides_list),204


@app.route('/api/v1/rides/<int:rideId>', methods=['PUT','PATCH','COPY','HEAD','OPTIONS','LINK','UNLINK','PURGE','LOCK','UNLOCK','PROPFIND','VIEW'])
def rider_id():
    return jsonify({}),405


@app.route('/api/v1/rides/<int:rideId>', methods=['GET'])
def ride_detail(rideId):
    #increment()
    #data = db.rides.find({'rideId': rideId})
    query = {'collection': 'rides','data':{'rideId': rideId}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text)
    
    if(len(rdata) > 0):
        #print('==========',rdata[0])
        dic = dict()
        dic = rdata[0]
        dic.pop("_id")
        return json.dumps(dic),200
    else:
        return 204



@app.route('/api/v1/rides/<int:rideId>', methods=['POST'])   
def join_ride(rideId):
    
    query = {'collection': 'rides','data':{ 'rideId': rideId}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text) 
        #print(rdata, rdata[0]['rideId'])

    if(len(rdata) > 0):
        #if(dbid.count() > 0):
            #db.rides.update({'rideId': rideId}, {'$push': {'joinee': name}} )
       query = {'collection': 'rides','work': 'update', 'data': ({'rideId': rideId},{'$push': {'users': name}} )}
       a = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)
            #return a.text

       return jsonify({}), 201
    else:
       return jsonify({}), 400



@app.route('/api/v1/rides/<int:rideId>', methods=['DELETE'])   
def delete_ride(rideId):
    #increment()
    query = {'collection': 'rides','data':{ 'rideId': rideId}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rdata = loads(rec.text) 

    if(len(rdata) > 0):
        query = {'collection': 'rides','work': 'delete', 'data':{ 'rideId': rideId}}
        rec = requests.post(url='http://52.4.226.187/api/v1/db/write',json=query)
        return jsonify({}), 200
    else:
        return jsonify({}), 400


@app.route('/api/v1/rides/count', methods=['PUT','POST','PATCH','COPY','DELETE','HEAD','OPTIONS','LINK','UNLINK','PURGE','LOCK','UNLOCK','PROPFIND','VIEW'])
def counter_no():
    return jsonify({}),405

@app.route('/api/v1/rides/count',methods=['GET'])
def rides_count():
    query = {'collection': 'rides','data':{}}
    rec = requests.post(url='http://52.4.226.187/api/v1/db/read',json=query)
    rides = loads(rec.text)
    rides_count = []
    rides_count.append(len(rides))
    return json.dumps(rides_count),200


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
   

