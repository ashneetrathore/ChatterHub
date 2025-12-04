"""
profile.py
Defines the Profile class
"""

import json, time, os
from pathlib import Path
from ds_messenger import DirectMessenger, DirectMessage

class DsuFileError(Exception):
    """
    DsuFileError is a custom exception handler raised when attempting to load or save Profile objects to file the system.
    """
    pass

class DsuProfileError(Exception):
    """
    DsuProfileError is a custom exception handler raised when attempting to deserialize a DSU file to a Profile object.
    """
    pass

class Profile:
    def __init__(self, dsuserver=None, username=None, password=None):
        '''
        Creates the following data attributes:
        dsuserver:str: the server to connect to
        username:str: user's username
        password:str: user's password
        recipients:list: the contacts the user adds
        sent_msgs:list: the direct messages the user has sent
        new_msgs:list: the unread direct messages the user has received
        retrievedmsgs:list: a collection of both sent and received messages, in order of time sent
        '''
        self.dsuserver = dsuserver # REQUIRED
        self.username = username # REQUIRED
        self.password = password # REQUIRED
        self._recipients = []   #OPTIONAL
        self._sentmsgs = []     #OPTIONAL
        self._newmsgs = []      #OPTIONAL
        self._retrievedmsgs = []    #OPTIONAL

    def send_msg(self, message, recipient) -> None:
        '''
        Sends a direct message to a user, and stores this message in a dictionary, appending to the _sentmsgs lists
        '''
        dmr = DirectMessenger(self.dsuserver, self.username, self.password)
        dmr.send(message, recipient)
        dm_dict = {'recipient': dmr.dm_obj.recipient,
                   'message': dmr.dm_obj.message,
                   'timestamp': dmr.dm_obj.timestamp
                   }
        self._sentmsgs.append(dm_dict)
        print(dm_dict)
        self._retrievedmsgs.append(dm_dict)
        
    def new_msg(self) -> None:
        '''
        Retrieves an unread message from another user, and stores this message in a dictionary, appending to the _newmsgs lists
        '''
        dmr = DirectMessenger(self.dsuserver, self.username, self.password)
        newmsg_list = dmr.retrieve_new()
        for i in range(0, len(newmsg_list)):
            dm_dict = {'from': newmsg_list[i].recipient,
                       'message': newmsg_list[i].message,
                       'timestamp': newmsg_list[i].timestamp
                       }
            self._newmsgs.append(dm_dict)
            print(dm_dict)
            self._retrievedmsgs.append(dm_dict)

    def save_profile(self, path: str) -> None:
        """
        save_profile accepts an existing dsu file to save the current instance of Profile to the file system.
        Example usage:
        profile = Profile()
        profile.save_profile('/path/to/file.dsu')
        Raises DsuFileError
        """
        p = Path(path)
        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'w')
                json.dump(self.__dict__, f)
                f.close()
            except Exception as ex:
                raise DsuFileError("An error occurred while attempting to process the DSU file.", ex)
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """
        load_profile will populate the current instance of Profile with data stored in a DSU file.
        Example usage: 
        profile = Profile()
        profile.load_profile('/path/to/file.dsu')
        Raises DsuProfileError, DsuFileError
        """
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                    
                for recipient in obj['_recipients']:
                    self._recipients.append(recipient)

                for msg in obj['_sentmsgs']:
                    dm_dict = {'recipient': msg['recipient'],
                               'message': msg['message'],
                               'timestamp': msg['timestamp']
                               }
                    self._sentmsgs.append(dm_dict)
        
                for msg in obj['_newmsgs']:
                    dm_dict = {'from': msg['from'],
                               'message': msg['message'],
                               'timestamp': msg['timestamp']
                               }
                    self._newmsgs.append(dm_dict)

                for msg in obj['_retrievedmsgs']:
                    if 'recipient' in msg.keys():
                        dm_dict = {'recipient': msg['recipient'],
                                   'message': msg['message'],
                                   'timestamp': msg['timestamp']
                                   }
                        self._retrievedmsgs.append(dm_dict)

                    if 'from' in msg.keys():
                        dm_dict = {'from': msg['from'],
                                   'message': msg['message'],
                                   'timestamp': msg['timestamp']
                                   }
                        self._retrievedmsgs.append(dm_dict)
                        
                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
