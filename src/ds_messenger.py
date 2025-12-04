"""
ds_messenger.py
Defines the DirectMessage and DirectMessenger classes
"""

import socket
import ds_protocol

# Replace with valid DSU server port
DSU_SERVER_PORT = 0

class DirectMessage:
    def __init__(self):
        """
        Creates the following data attributes: recipient, message, and timestamp.
        """
        self.recipient = None
        self.message = None
        self.timestamp = None


class DirectMessenger:
    def __init__(self, dsuserver=None, username=None, password=None):
        """
        Creates the following data attributes: token, dsuserver, port, username, password, dm_obj.
        Populates token attribute to token returned from server upon joining.
        """
        self.token = None
        self.dsuserver = dsuserver
        self.port = DSU_SERVER_PORT
        self.username = username
        self.password = password
        self.token = self._join_serv()
        self.dm_obj = None

    def _publish(self, soc, msg_type):
        """
        Sends information to the server, and returns the response the server gives.
        """
        send = soc.makefile('w')
        recv = soc.makefile('r')
        send.write(msg_type + '\r\n')
        send.flush()
        resp = recv.readline()
        return resp

    def _join_serv(self):
        """
        Joins the server and returns token generated from response message.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((self.dsuserver, self.port))
                join_msg = ds_protocol.join(self.username, self.password)
                resp = self._publish(soc, join_msg)
                rt = ds_protocol.extract_json(resp)
                if rt[0] == "error":
                    print(rt[1])
                else:
                    return ds_protocol.token
        except OSError:
            print("ERROR: Host is unreachable. Check WiFi, IP address, and port.")
        except (ConnectionRefusedError, OverflowError, TimeoutError, socket.gaierror, TypeError):
            print("ERROR: IP address or port is invalid.")
        except Exception as r_error:
            print(rt[1])
                
            
    def send(self, message:str, recipient:str) -> bool:
        """
        Sends a direct message to another user and populates a DirectMessage object.
        Returns true if message successfully sent, false if send failed.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((self.dsuserver, self.port))
                dir_msg = ds_protocol.direct_message(message, recipient)
                resp = self._publish(soc, dir_msg)
                rt = ds_protocol.extract_json(resp)
                if rt[0] == "error":
                    print(rt[1])
                    raise Exception(r_error)
                else:
                    dm = DirectMessage()
                    dm.recipient = recipient
                    dm.message = message
                    dm.timestamp = ds_protocol.timestamp
                    self.dm_obj = dm
                    return True
        except OSError:
            print("ERROR: Host is unreachable. Check WiFi, IP address, and port.")
            return False
        except (ConnectionRefusedError, OverflowError, TimeoutError, socket.gaierror, TypeError):
            print("ERROR: IP address or port is invalid.")
            return False
        except Exception as r_error:
            print(rt[1])
            return False
            

    def _populate(self, msg_dict, dm_obj):
        """
        Populates the data attributes of DirectMessage with data from each message dictionary.
        Returns the newly populated DirectMessage obj.
        """
        dm_obj.recipient = msg_dict['from']
        dm_obj.message = msg_dict['message']
        dm_obj.timestamp = msg_dict['timestamp']
        return dm_obj

    def retrieve_new(self) -> list:
        """
        Retrieves new messages from DS server.
        Returns a list of DirectMessage objects containing all new messages.
        """
        try:
            newmsg_list = []
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((self.dsuserver, self.port))
                new_msg = ds_protocol.new_message()
                resp = self._publish(soc, new_msg)
                rt = ds_protocol.extract_messages(resp)
            for msg_dict in rt.message:
                dm = DirectMessage()
                dm = self._populate(msg_dict, dm)
                newmsg_list.append(dm)
            return newmsg_list
        except OSError:
            print("ERROR: Host is unreachable. Check WiFi, IP address, and port.")
        except (ConnectionRefusedError, OverflowError, TimeoutError, socket.gaierror, TypeError):
            print("ERROR: IP address or port is invalid.")
        except Exception as r_error:
            print(rt[1])
    
    def retrieve_all(self) -> list:
        """
        Retrieves all messages from DS server.
        Returns a list of DirectMessage objects containing all messages.
        """
        try:
            self.allmsg_list = []
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((self.dsuserver, self.port))
                all_msg = ds_protocol.all_message()
                resp = self._publish(soc, all_msg)
                rt = ds_protocol.extract_messages(resp)
            for msg_dict in rt.message:
                dm = DirectMessage()
                dm = self._populate(msg_dict, dm)
                self.allmsg_list.append(dm)
            return self.allmsg_list
        except OSError:
            print("ERROR: Host is unreachable. Check WiFi, IP address, and port.")
        except (ConnectionRefusedError, OverflowError, TimeoutError, socket.gaierror, TypeError):
            print("ERROR: IP address or port is invalid.")
        except Exception as r_error:
            print(rt[1])
