"""
ds_protocol.py
Handles encoding and decoding of JSON messages for the distributed social messenger
"""

import json, time
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages
DataTuple = namedtuple('DataTuple', ['type','message'])
'''
DataTuple: {string, string}
'''

def extract_json(json_msg:str) -> DataTuple:
  '''
  Calls the json.loads function on a json string (join command) and converts it to a DataTuple object
  '''
  try:
    json_obj = json.loads(json_msg)
    type = json_obj['response']['type']
    message = json_obj['response']['message']
    if 'token' in str(json_obj):
      # Globally set token to use for other commands
      global token
      token = json_obj['response']['token'] 
  except json.JSONDecodeError:
    print("JSON cannot be decoded.")
  return DataTuple(type, message)

def extract_messages(json_msg:str) -> DataTuple:
  '''
  Calls the json.loads function on a json string (direct message command) and converts it to a DataTuple object
  '''
  try:
    json_obj = json.loads(json_msg)
    type = json_obj['response']['type']
    message = json_obj['response']['messages']
  except json.JSONDecodeError:
    print("JSON cannot be decoded.")
  return DataTuple(type, message)

  
def join(username, password):
  '''
  Wraps join command in JSON format
  '''
  join_msg = {"join": {"username": username,
                       "password": password,
                       "token":""
                       }}
  return json.dumps(join_msg)

def direct_message(msg, o_user):
  '''
  Wraps direct message send command in JSON format
  '''
  dir_msg = {"token": token,
             "directmessage": {"entry": msg,
                               "recipient": o_user,
                               "timestamp": time.time()
                               }}
  # Globally sets the timestamp to store for data in Direct Message class
  global timestamp
  timestamp = dir_msg['directmessage']['timestamp'] 
  return json.dumps(dir_msg)

 
def new_message():
  '''
  Wraps direct message retrieve new command in JSON format
  '''
  new_msg = {"token": token,
             "directmessage": "new"
             }
  return json.dumps(new_msg)

def all_message():
  '''
  Wraps direct message retrieve all command in JSON format
  '''
  all_msg = {"token": token,
             "directmessage": "all"
             }
  return json.dumps(all_msg)
