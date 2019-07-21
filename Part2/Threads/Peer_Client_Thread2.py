import threading
import time
import socket
import pickle
import random
from Part2.Peer.Peer2 import *
from Part2.Threads.PDU2 import *
import pickle
import hashlib
import signal


class Peer_Client_Thread2(threading.Thread):
    local_peer = None
    hash_function = None

    def __init__(self, peer):
        threading.Thread.__init__(self)
        self.local_peer = peer
        self.hash_function = hashlib.sha1()
        # signal.signal(signal.SIGINT, self.signal_handler)
    #
    # def signal_handler(signal, frame):
    #     print("ahyyy")
    #     pass

    def run(self):
        while True:
            try:
                # get peer message from CLI interface
                remote_peer = input("-Local peer: Enter Peer you want to send a message to, in IP:Port Format, or enter Q to exit")
                if remote_peer == "Q" or remote_peer == "q":
                    self.local_peer.stop_local_peer = True
                    print("-Local Peer: Client Thread Stopped")
                    break
                message = input("-Local Peer: Enter Message")

                # check if peer in chord network
                self.hash_function.update(remote_peer.encode())
                remote_peer_CID = self.hash_function.hexdigest()
                remote_found = False
                for x in self.local_peer.chord_net_peers:
                    if x['id'] == remote_peer_CID:
                        remote_found = True
                        remote_peer_ip, remote_peer_port = remote_peer.split(':')

                      # establish connection to remote peer and send message
                        random_port_once = random.randint(30000, 60000)
                        socket_once =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                        socket_once.bind((self.local_peer.local_host_ip, int(random_port_once)))
                        socket_once.connect((remote_peer_ip, int(remote_peer_port)))

                        # prepare message
                        pdu = PDU2(1, "message", self.local_peer.TTL, self.local_peer.local_peer_CID, self.local_peer.local_host_ip, self.local_peer.local_host_port, message, "Dumb Message ")
                        picled_pdu = pickle.dumps(pdu)
                        socket_once.send(picled_pdu)
                        print("-Local Peer: Message Sent To Peer with ID: " + x['id'] + ", IP: " + remote_peer_ip + ", Port: " + remote_peer_port)
                    # close socket once when finished sending
                        socket_once.shutdown(2)
                        break
                if not remote_found:
                    # try to send it to successor
                    # check for successor and predecessor
                    if int(remote_peer_CID, 16) < int(self.local_peer.successor, 16):
                        # establish connection to remote peer and send message
                        random_port_once = random.randint(30000, 60000)
                        socket_once = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                        socket_once.bind((self.local_peer.local_host_ip, int(random_port_once)))
                        socket_once.connect((remote_peer_ip, int(remote_peer_port)))

                        # prepare message
                        pdu = PDU2(1, "message", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                   self.local_peer.local_host_ip, self.local_peer.local_host_port, message,
                                   "Dumb Message ")
                        picled_pdu = pickle.dumps(pdu)
                        socket_once.send(picled_pdu)
                        print("-Local Peer: Message Sent To Peer with ID: " + x[
                            'id'] + ", IP: " + remote_peer_ip + ", Port: " + remote_peer_port)
                        # close socket once when finished sending
                        socket_once.shutdown(2)
                        break
                        pass
                    elif int(remote_peer_CID, 16) > int(self.local_peer.predecessor):
                        # establish connection to remote peer and send message
                        random_port_once = random.randint(30000, 60000)
                        socket_once = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                        socket_once.bind((self.local_peer.local_host_ip, int(random_port_once)))
                        socket_once.connect((remote_peer_ip, int(remote_peer_port)))

                        # prepare message
                        pdu = PDU2(1, "message", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                   self.local_peer.local_host_ip, self.local_peer.local_host_port, message,
                                   "Dumb Message ")
                        picled_pdu = pickle.dumps(pdu)
                        socket_once.send(picled_pdu)
                        print("-Local Peer: Message Sent To Peer with ID: " + x[
                            'id'] + ", IP: " + remote_peer_ip + ", Port: " + remote_peer_port)
                        # close socket once when finished sending
                        socket_once.shutdown(2)
                        break
                        pass
                    else:
                        print("-Local Peer: Entered Remote Peer Not In Chord Network")
                time.sleep(1)

            except KeyboardInterrupt:
                print("CLI Thread Stopped")
                exit()