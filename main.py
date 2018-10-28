import sys
import json
import socket
import threading
import time
from datetime import datetime
import magic


backlog = 10
buffer_size = 4048

docroots = {}

class Server(threading.Thread):

    def __init__(self, ip,port):
        super().__init__()
        self.ip = ip
        self.port = port


    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.ip, self.port))

            #print("Listening on TCP {}:{}".format(*sock.getsockname()))
            sock.listen(backlog)

            while True:
                conn, addr = sock.accept()

                Worker(conn, buffer_size).start()


def parse_config_file(file_name):

    servers_started  = []

    with open(file_name) as f:
        data = json.load(f)

    for elem in data["server"]:
        docroots[elem["vhost"]] = elem["documentroot"]
        if([elem["ip"],elem['port']] not in servers_started):

         Server(elem["ip"],elem["port"]).start()
         #print("server " + str(elem["port"]) + " started")
         servers_started.append([elem["ip"],elem['port']])






parse_config_file(sys.argv[1])





class Worker(threading.Thread):

    def __init__(self, sock, buffer_size):

        super().__init__()

        self.sock = sock
        self.buffer_size = buffer_size
        self.method = ""
        self.file_name = ""
        self.v_host = ""
        self.keep_alive = False
        self.file = ""
        self.status_code = 200
        self.range = ""


    def parse_header(self,header):


       tokens = header.split("\r\n")

       self.method = tokens[0].split(" ")[0].strip()
       self.file_name = tokens[0].split(" ")[1].replace("%5C", "/").replace("%20", " ").strip()

       for elem in tokens[1:]:
           if("host" in elem.lower()):
               self.v_host = elem.split(":")[1].strip()
           elif("connection" in elem.lower() and "keep-alive" in elem.lower()):
               self.keep_alive = True
           elif("range" in elem.lower()):

               self.range = elem.split("=")[1].strip()

       try:

           with open(docroots[self.v_host] + "/" + self.file_name, 'rb') as file:
               if (self.range != ""):

                   offset = int(self.range.split("-")[0])
                   file.seek(offset)
                   if(self.range.split("-")[1] == ""):
                       self.file = file.read()
                   else:
                       length = int(self.range.split("-")[1]) - offset +1
                       self.file = file.read(length)
               else:
                   self.file = file.read()



       except:
           pass


    def make_responce_header(self):

        response = "HTTP/1.1 "
        domain_not_found = "<html><body><p>REQUESTED DOMAIN NOT FOUND</p></body></html>"
        if(len(self.file) !=0):
            self.status_code = 200

            response+="200 OK"
        else:
            self.status_code = 404
            response+="404 Not Found"

        response+="\r\n"

        response+="Date: " +datetime.today().strftime('%Y-%m-%d') + "\r\n"

        response+="Server: my server" + "\r\n"

        if(self.status_code == 200):
          response+="Content-Length: "+str(len(self.file))+"\r\n"
        else:
            response += "Content-Length: " + str(len(domain_not_found)) + "\r\n"





        response+="Accept-Ranges: bytes" +"\r\n"
        if(self.file !=""):
            mime = magic.Magic(mime=True)
            type = mime.from_file(self.v_host+"/"+self.file_name)

            response += "Content-Type: "+type+"\r\n"
        else:

            response += "Content-Type: plain/html" + "\r\n"

        if(self.keep_alive):
           response+="Connection: keep-alive"+"\r\n"
           response+="Keep-Alive: timeout=5, max=1000" + "\r\n"





        response+="ETag: 12"+"\r\n"

        if(self.status_code == 404):
            response+="\r\n"
            response+=domain_not_found




        return response


    def run(self):

        while True:
            try:
                payload = self.sock.recv(self.buffer_size)
            except:
                #print("timeout out")
                break






            payload_str = str(payload, "utf-8").strip()
            #print("res --------",payload_str)



            #responce["content"] = self.file

            if payload:

                #print("{}:{} > {}".format(peer_name[0], peer_name[1], payload_str))

                if payload_str == "OVER":

                    #print("Client closed connection: {}".format(peer_name))
                    self.sock.close()
                    break
                else:


                        self.parse_header(payload_str)

                        responce = self.make_responce_header()



                        #self.sock.send("\r\n".encode())

                        if(self.method == "GET"):

                           if(self.status_code == 200):
                               responce += "\r\n"
                               self.sock.send(responce.encode())

                               self.sock.send(self.file)
                           elif(self.status_code == 404):

                               responce+="\r\n"
                               self.sock.send(responce.encode())


                        else:

                            if (self.status_code == 200):
                                responce += "\r\n"
                                self.sock.send(responce.encode())

                            elif (self.status_code == 404):

                                responce += "\r\n"
                                self.sock.send(responce.encode())

                                self.sock.send(responce.encode())




                        if (self.keep_alive and self.sock.gettimeout() == None):

                            self.sock.settimeout(5)

            else:
                #print("Client closed connection: {}".format(peer_name))
                break






