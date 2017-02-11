'''
    Simple socket server using threads
'''
import socket
from public_functions import *
import sys
import json
from thread import *
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import urllib

jsonData = {}

with open("data/"+"S"+'.json') as data_file:
    jsonData["S"] = json.load(data_file)
with open("data/"+"F"+'.json') as data_file:
    jsonData["F"] = json.load(data_file)
with open("data/"+"M1"+'.json') as data_file:
    jsonData["M1"] = json.load(data_file)
with open("data/"+"M2"+'.json') as data_file:
    jsonData["M2"] = json.load(data_file)
with open("data/"+"S"+'.json') as data_file:
    jsonData["S"] = json.load(data_file)


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

# This is the server part
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8000 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((socket.gethostname(), PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print ('Socket bind complete')
 
# Start listening on socket
s.listen(10)
print ('Socket now listening')

#Function for handling connections. This will be used to create threads
def processrequest(requestdict):
    pass




def clientthread(conn):
    #Sending message to connected client
    # conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Receiving from client
        data = conn.recv(1024)
        if not data: 
            break
        request = HTTPRequest(data)
        path = request.path

        response_headers = {
            'Content-Type': 'text',
            'Connection': 'close',
        }

        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.items())

        response_proto = 'HTTP/1.1'
        response_status = '200'
        response_status_text = 'OK' # this can be random

        # sending all this stuff
        r = '%s %s %s\n' % (response_proto, response_status, response_status_text)
        conn.send(r.encode(encoding="utf-8"))
        conn.send(response_headers_raw.encode(encoding="utf-8"))

        conn.send('\n'.encode(encoding="utf-8")) # to separate headers from body
        if path[1:6] == "info:":
            conn.send(str(json.dumps(jsonData["S"]["courses"][path[6:]])))
        elif path[1:10] == "schedule:":
            unquoted = urllib.unquote(path[10:])
            j = json.loads(unquoted)
            courseMust = j["coursesMust"]
            courseOptional = j["coursesOptional"]
            semester = j["semester"]
            numberOfOptionals = j["numberOfOptionals"]
            sortingType = j["sort"]
            filter = j["filter"]
            filter["lunchtime"].append(1)
            top = j["top"]


            g = getPossibleSchedules(courseMust,courseOptional,semester,numberOfOptionals)
            if sortingType == "compact":
                g = sortSchedulesByCompactness(g,semester)

            afterFilter = filterSchedules(g,semester,filter)
            result = []
            for i in range(top):
                cur = afterFilter[i]
                result.append(produceFullInfoForSchedule(cur,semester))
            conn.send(json.dumps(result).encode(encoding = "utf-8"))
        elif path[1:5] == "fce:":
            conn.send(json.dumps(fceReturn(path[5:])).encode(encoding = "utf-8"))
        break


        # conn.close()
     
        # conn.sendall(reply)
     
    #came out of loop
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
s.close()

    
