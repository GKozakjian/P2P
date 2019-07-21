import threading
import time
import socket

import random
import hashlib
from Part2.Peer.Peer2 import *
import pickle
from Part2.Threads.PDU2 import *


class Peer_Server_Thread2(threading.Thread):
    local_peer = None
    hash_function = None

    def __init__(self, peer):
        threading.Thread.__init__(self)
        self.local_peer = peer
        self.hash_function = hashlib.sha1()

    def run(self):
        self.local_peer.local_peer_tcp_socket.listen(1)
        print("-Local Peer: Started Listening On Bound Socket")
        self.start_receiving()

    def start_receiving(self):
        while True:
            try:
                if self.local_peer.stop_local_peer:
                    print("-Local Peer: Server Thread Stopped")
                    break

                # accept new connection
                established_tcp_connection, established_tcp_connection_address = self.local_peer.local_peer_tcp_socket.accept()
                print()
                print("-Local Peer: Accepted New TCP Connection With Remote Peer: " + str(
                    established_tcp_connection_address))

                received_data = established_tcp_connection.recv(4096)
                received_pdu = pickle.loads(received_data)

                # if received message is a message from a peer in chrod network
                if received_pdu['type'] == "message":
                    received_peer_CID = received_pdu['id']
                    for x in self.local_peer.chord_net_peers:
                        if x['ID'] == received_peer_CID:
                            print("-Local Peer: Received Message: " + received_pdu['message'] + ", From Pere: " +
                                  established_tcp_connection[0] + ":" + established_tcp_connection[1])
                            break

                # new node joined by other peers
                elif received_pdu['type'] == "newnodejoin":
                    # add new node to the chord array
                    new_node_info = received_pdu['message']
                    # add peer to chord network
                    new_chord_peer = \
                        {
                            "id": new_node_info['id'],
                            "ip": new_node_info['ipv4'],
                            "port": new_node_info['port']
                        }
                    self.local_peer.chord_net_peers.append(new_chord_peer)

                    # check for successor and predecessor
                    if int(received_join_CID, 16) < int(self.local_peer.successor, 16):
                        self.local_peer.successor = received_join_CID
                    if int(received_join_CID, 16) > int(self.local_peer.predecessor):
                        self.local_peer.predecessor = received_join_CID

                    print("-Local Peer: New Node Joined Chord Network with ID: " + new_node_info['id'] + ", IP:" +
                          new_node_info['ipv4'] + "  And Port: " + new_node_info['port'])

                # if received message is join request
                elif received_pdu['type'] == "join":
                    # if static ID exist in join request
                    if received_pdu['id'] is not None:
                        received_join_CID = received_pdu['id']
                        # check for collision
                        for x in self.local_peer.chord_net_peers:
                            if x['id'] == received_join_CID:
                                # generate new ID based on remote peer IPv4 and Port
                                received_join_peer_socket = received_pdu['ipv4'] + ":" + received_pdu['port']
                                self.hash_function.update(received_join_peer_socket.encode())
                                received_join_CID = self.hash_function.hexdigest()
                        # add peer to chord network
                        new_chord_peer = \
                            {
                                "id": received_join_CID,
                                "ip": received_pdu['ipv4'],
                                "port": received_pdu['port']
                            }
                        self.local_peer.chord_net_peers.append(new_chord_peer)

                        # check for successor and predecessor
                        if int(received_join_CID, 16) < int(self.local_peer.successor, 16):
                            self.local_peer.successor = received_join_CID
                        if int(received_join_CID, 16) > int(self.local_peer.predecessor):
                            self.local_peer.predecessor = received_join_CID

                        print("-Local Peer: New Node Joined Chord Network with ID: " + received_join_CID + ", IP:" +
                              received_pdu['ipv4'] + "  And Port: " + received_pdu['port'])
                        if received_join_CID != received_pdu['id']:
                            msg = \
                                {
                                    'id': received_join_CID
                                }
                            join_reply_pdu = PDU2(1, "joinack", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                                  self.local_peer.local_host_ip, self.local_peer.local_host_port, msg,
                                                  "")
                            serialized_join_reply = pickle.dumps(join_reply_pdu)
                            established_tcp_connection.send(serialized_join_reply)
                        else:
                            join_reply_pdu = PDU2(1, "joinackid", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                                  self.local_peer.local_host_ip, self.local_peer.local_host_port, "",
                                                  "")
                            serialized_join_reply = pickle.dumps(join_reply_pdu)
                            established_tcp_connection.send(serialized_join_reply)

                        # notify chord network that a new node joined
                        # establish connection to remote peer and send message
                        random_port_once = random.randint(30000, 60000)
                        socket_once = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        socket_once.bind((self.local_peer.local_host_ip, int(random_port_once)))

                        message = \
                            {
                                'id': received_join_CID,
                                'ip': received_pdu['ipv4'],
                                'port': received_pdu['port']
                            }
                        for x in self.local_peer.chord_net_peers:
                            if x['id'] != received_join_CID or x['id'] != self.local_peer.local_peer_CID:
                                socket_once.connect((x['ip'], int(x['port'])))

                                # prepare message
                                pdu = PDU2(1, "newnodejoin", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                           self.local_peer.local_host_ip, self.local_peer.local_host_port, message, "")
                                picled_pdu = pickle.dumps(pdu)
                                socket_once.send(picled_pdu)

                                # close socket once when finished sending
                                socket_once.shutdown(2)

                    # if there is no static ID in join request
                    else:
                        received_join_peer_socket = received_pdu['ipv4'] + ":" + received_pdu['port']
                        self.hash_function.update(received_join_peer_socket.encode())
                        received_join_CID = self.hash_function.hexdigest()

                        for x in self.local_peer.chord_net_peers:
                            # check if node already exist in chord network
                            if x['id'] == received_join_CID:
                                break
                            # join new node to chord net if it doesnt exist in network
                            else:
                                new_chord_peer = \
                                    {
                                        "id": received_join_CID,
                                        "ip": received_pdu['ipv4'],
                                        "port": received_pdu['port']
                                    }
                                self.local_peer.chord_net_peers.append(new_chord_peer)
                                print(
                                    "-Local Peer: New Node Joined Chord Network with ID: " + received_join_CID + ", IP:" +
                                    received_pdu['ipv4'] + "  And Port: " + received_pdu['port'])

                                msg = \
                                    {
                                        "id": received_join_CID
                                    }
                                join_reply_pdu = PDU2(1, "joinack", self.local_peer.TTL, self.local_peer.local_peer_CID,
                                                      self.local_peer.local_host_ip, self.local_peer.local_host_port,
                                                      msg, "")
                                serialized_join_reply = pickle.dumps(join_reply_pdu)
                                established_tcp_connection.send(serialized_join_reply)

                                # notify chord network that a new node joined
                                # establish connection to remote peer and send message
                                random_port_once = random.randint(30000, 60000)
                                socket_once = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                socket_once.bind((self.local_peer.local_host_ip, int(random_port_once)))

                                message = \
                                    {
                                        'id': received_join_CID,
                                        'ip': received_pdu['ipv4'],
                                        'port': received_pdu['port']
                                    }
                                for x in self.local_peer.chord_net_peers:
                                    if x['id'] != received_join_CID:
                                        socket_once.connect((x['ip'], int(x['port'])))

                                        # prepare message
                                        pdu = PDU2(1, "newnodejoin", self.local_peer.TTL,
                                                   self.local_peer.local_peer_CID,
                                                   self.local_peer.local_host_ip, self.local_peer.local_host_port,
                                                   message, "")
                                        picled_pdu = pickle.dumps(pdu)
                                        socket_once.send(picled_pdu)

                                        # close socket once when finished sending
                                        socket_once.shutdown(2)

                time.sleep(10)
            except Exception as e:
                print("im fucking here")
                print(e)
                pass
                # print("-Local Peer: No New Incoming Connections")
