import decimal
import boto3
import datetime
##you're going to need to rename this file to 

from flask import Flask
import os
from flask import request
import json

application = Flask(__name__)
application.config.update(os.environ)

##this sets up the dynamo db module, and the connection. Depedending on what sever site you set up the api on, 
dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url="https://dynamodb.us-east-2.amazonaws.com")
print ("db = {}".format(dynamodb))
##HASH_LOOKUP is the table name
table = dynamodb.Table('HASH_LOOKUP')
clock = datetime.datetime

##decimal formating fuction for the Json conversion
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


##queries in the dynamo db table
def table_lookup(h):
    ##looks up the information for the given hash
    response = table.get_item(Key = {'SENTENCE_HASH': h})
    try:
        item = response['Item']
    ##if there is no hash then just return generic nothing information
    except KeyError:
       item  = {'SENTENCE_HASH' : h, 'COUNTS' : 0, 'TIMES':[]}
    #print(item)
    return item

##this is the webcall that you would use. ex. something.com/lookup/hash
@application.route('/lookup', methods=['POST'])
def sentnece_lookup():
    sentence = request.form['PHRASE']
    output = table_lookup(sentence)
    return json.dumps(output, default= decimal_default)

##just makes sure that the server is up and running
@application.route('/health')
def health():
    return 'healthy'

##the main method that amazon will run to spin up the sever
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000, threaded=True, debug=True)
