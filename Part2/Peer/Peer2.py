import sys
import socket
from Part2.Threads.Peer_Client_Thread2 import *
from Part2.Threads.Peer_Server_Thread2 import *
import random
from pickle import *
import hashlib
from Part2.Peer.PDU2 import *

class Peer2:
    successor = None
    predecessor = None
    local_host_ip = None
    local_host_port = None
    local_peer_CID = None
    local_peer_tcp_socket = None
    local_peer_server_thread = None
    local_peer_client_thread = None
    local_peer_cli_thread = None
    chord_net_peers = []
    latest_remote_peer_ip = None
    latest_remote_peer_port = None
    TTL = None
    hash_function = None
    stop_local_peer = False


    def __init__(self, opcode, remote_peer_ip_port, SID_Option, CSID, TTL_Option, TTL):
        try:
            self.message_available_to_send = False
            self.local_peer_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.local_host_ip = "localhost"
            self.hash_function = hashlib.sha1()

            # bind the socket
            self.bind_socket()

            # check opcode, and act accordingly
            if opcode == '-p':
                self.latest_remote_peer_ip, self.latest_remote_peer_port = remote_peer_ip_port.split(':')
                if SID_Option == "-I":
                    self.local_peer_CID = CSID
                    if TTL_Option == "-t":
                        self.TTL = TTL
                    else:
                        self.TTL = 255
                else:
                    self.local_peer_CID = ""
                    if TTL_Option == "-t":
                        self.TTL = TTL
                    else:
                        self.TTL = 255

                self.join_chord()

            elif opcode == "-I":
                self.local_peer_CID = CSID
                if TTL_Option == "-t":
                    self.TTL = TTL
                else:
                    self.TTL = 255
                # create new chord network
                self.create_new_chord()
            else:
                if opcode == "-t":
                    self.TTL = TTL
                else:
                    self.TTL = 255
                # create new chord network
                self.create_new_chord()

            # start local peer's sender and receiver threads
            self.assign_threads()

            # join the threads
            self.join_threads()

            # both trheads stopped
            print("-Local Peer: Started Chord Leave Process")
            # establish connection to remote peer and send message
            random_port_once = random.randint(30000, 60000)
            socket_once = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_once.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_once.bind((self.local_host_ip, int(random_port_once)))

            for x in self.chord_net_peers:
                if x['id'] != self.local_peer_CID:
                    socket_once.connect((x['ip'], int(x['port'])))

                    # prepare message
                    pdu = PDU2(1, "leave", self.TTL, self.local_peer_CID,
                               self.local_host_ip, self.local_host_port, "By Bcs")
                    picled_pdu = pickle.dumps(pdu)
                    socket_once.send(picled_pdu)
                    print("-Local Peer: Leave Request Sent to Peer with ID: " + x['id'] + ", IP: " + x['ip'] + ", Port: " + x['port'])
                    # close socket once when finished sending
                    socket_once.shutdown(2)
            print("-Local Peer: Stopped")
            sys.exit()
        except KeyboardInterrupt:
            # disconnect from network
            print(" by by im going home")
            pass



    def bind_socket(self):
        # Generate a random socket  for local host
        self.local_host_port = random.randint(30000, 60000)
        self.local_peer_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.local_peer_tcp_socket.settimeout(10)
        self.local_peer_tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.local_peer_tcp_socket.bind((self.local_host_ip, self.local_host_port))
        print("-Local Peer: Socket Bind Completed On IP: " + self.local_host_ip + " & Port: " + str(self.local_host_port))

    def assign_threads(self):
        self.local_peer_client_thread = Peer_Client_Thread2(self)
        self.local_peer_server_thread = Peer_Server_Thread2(self)
        print("-Local Peer: Sender & Receiver Threads Started")
        self.local_peer_server_thread.start()
        self.local_peer_client_thread.start()


    def join_threads(self):
        self.local_peer_client_thread.join()
        self.local_peer_server_thread.join()

    def join_chord(self):
        try:
            # send join message to join a chord network
            join_pdu = PDU2(1, "join", self.TTL, self.local_peer_CID, self.local_host_ip, self.local_host_port, "join the network", "")
            serialized_pdu = pickle.dumps(join_pdu, pickle.HIGHEST_PROTOCOL)
            serialized_join_pdu = pickle.dumps(join_pdu, pickle.HIGHEST_PROTOCOL)

            self.local_peer_tcp_socket.connect((self.latest_remote_peer_ip, int(self.latest_remote_peer_port)))
            self.local_peer_tcp_socket.send(serialized_join_pdu)
        except Exception as e:
            print(e)

        # receive join confirm
        while True:
            try:
                join_reply_pdu = self.local_peer_tcp_socket.recv(1024)
                serialized_join_reply_pdu = pickle.loads(join_reply_pdu)
                if serialized_join_reply_pdu['type'] == "joinackid":
                    new_chord_peer = \
                        {
                            "id": serialized_join_reply_pdu['id'],
                            "ip": serialized_join_reply_pdu['ipv4'],
                            "port": serialized_join_reply_pdu['port']
                        }
                    self.chord_net_peers.append(new_chord_peer)
                    print("-Local Peer: Joined Chord Network With Static ID")
                elif serialized_join_reply_pdu['type'] == 'joinack':
                    reply_CID_message = serialized_join_reply_pdu['message']
                    self.local_peer_CID = reply_CID_message['id']
                    new_chord_peer = \
                        {
                            "id": serialized_join_reply_pdu['id'],
                            "ip": serialized_join_reply_pdu['ipv4'],
                            "port": serialized_join_reply_pdu['port']
                        }
                    self.chord_net_peers.append(new_chord_peer)

                    print("-Local Peer: Joined Chord Network With New Generated ID")
                    break
            except:
                print("-Local Peer: Still Waiting for Join Reply")


    def create_new_chord(self):
        print("-Local Peer: New Chord Network Created")
        if self.local_peer_CID is None:
            cid_gen_str = self.local_host_ip + ":" + str(self.local_host_port)
            self.local_peer_CID = self.hash_function.update(cid_gen_str.encode())
            self.local_peer_CID = self.hash_function.hexdigest()
        new_chord_peer = \
            {
                "id": self.local_peer_CID,
                "ip": self.local_host_ip,
                "port": self.local_host_port
            }
        self.chord_net_peers.append(new_chord_peer)
        print("-Local Peer: Joined Chord Network With Chord ID: " + str(self.local_peer_CID))


if __name__ == "__main__":
    option = sys.argv[1]
    if option == '-p':
        if sys.argv[3] == "-I":
            p = Peer2(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        else:
            p = Peer2(sys.argv[1], sys.argv[2], "", "", sys.argv[3], sys.argv[4])
    elif option == '-I':
        p = Peer2(sys.argv[1], sys.argv[2], "", "", sys.argv[3], sys.argv[4])
    elif option == "-t":
        p = Peer2(sys.argv[1], "", "", "", "", sys.argv[2])
