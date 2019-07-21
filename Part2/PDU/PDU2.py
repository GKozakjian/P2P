

class PDU2():
    version = ""
    ttl = 0
    id = ""
    Port = 0
    ipv4 = ""
    type = ""
    message = ""
    reserved = ""


    def __init__(self, version, type, ttl, ID, ipv4, port, message, reserved):
        self.version = version
        self.ttl = ttl
        self.id = ID
        self.Port = port
        self.ipv4 = ipv4
        self.type = type
        self.message = message
        self.reserved = reserved

