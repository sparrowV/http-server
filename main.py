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
                #print("New connection: {}".format(addr))
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
    #print("doc root\n\n",docroots)



    #print(data)

parse_config_file(sys.argv[1])





class Worker(threading.Thread):

    def __init__(self, sock, buffer_size):
        #print("starint bor\n\n")
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
       # #print("start\n")

       tokens = header.split("\r\n")
       """
       # #print("tokens",tokens)
        self.method = tokens[0].split(" ")[0].strip()
        ##print(self.method)


        self.file_name = tokens[0].split(" ")[1].replace("%5C","/").replace("%20"," ").strip()
        ##print(self.file_name)
        self.v_host = tokens[1].split(":")[1].strip()
        ##print(self.v_host)



        if("keep-alive" in tokens[5] or "keep-alive" in tokens[4]):

            self.keep_alive = True
       # #print(self.keep_alive)

        try:
            #print("vhost is \n",self.v_host)
            #print("here path is \n "+docroots[self.v_host])
            with open(docroots[self.v_host]+"/" + self.file_name, 'rb') as file:

                self.file = file.read()
        except:
            pass
            #print("eroor reading file")

        """
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
           # print("vhost is \n",self.v_host)
           # print("here path is \n "+docroots[self.v_host])
           with open(docroots[self.v_host] + "/" + self.file_name, 'rb') as file:

               self.file = file.read()
       except:
           pass
           # print("eroor reading file")

    def make_responce_header(self):

        response = "HTTP/1.1 "
        domain_not_found = "<html><body><p>REQUESTED DOMAIN NOT FOUND</p></body></html>"
        if(len(self.file) !=0):
            self.status_code = 200
            #print("status code in responce",self.status_code)
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


        #print("file_name",self.file_name)
        #print(self.file_name.split("."))

        if(self.file !=""):
            mime = magic.Magic(mime=True)
            type = mime.from_file(self.v_host+"/"+self.file_name)
            #print("type",type)
            response += "Content-Type: "+type+"\r\n"
        else:
            #print("of couse\n\n\n\n\n")
            response += "Content-Type: plain/html" + "\r\n"





        response+="ETag: 12"+"\r\n"

        if(self.status_code == 404):
            response+="\r\n"
            response+=domain_not_found




        return response


    def run(self):
        #print("zd\n\n")
        peer_name = self.sock.getpeername()



        while True:
           # self.sock.settimeout(10)
            #print("in while")


            try:
                payload = self.sock.recv(self.buffer_size)
            except:
                #print("timeout out")
                break





            #print("sd")
            payload_str = str(payload, "utf-8").strip()




            #responce["content"] = self.file

            if payload:
                #print("in here")
                #print("{}:{} > {}".format(peer_name[0], peer_name[1], payload_str))

                if payload_str == "OVER":
                    #print("over\n\n\n?")
                    #print("Client closed connection: {}".format(peer_name))
                    self.sock.close()
                    break
                else:


                        self.parse_header(payload_str)

                        responce = self.make_responce_header()



                        #self.sock.send("\r\n".encode())

                        if(self.method == "GET"):
                           #print("in get",self.status_code)
                           if(self.status_code == 200):
                               responce += "\r\n"
                               self.sock.send(responce.encode())

                               self.sock.send(self.file)
                           elif(self.status_code == 404):

                               responce+="\r\n"
                               self.sock.send(responce.encode())
                               #print("here bitch")

                        else:
                            #print("in head", self.status_code)
                            if (self.status_code == 200):
                                responce += "\r\n"
                                self.sock.send(responce.encode())

                            elif (self.status_code == 404):

                                responce += "\r\n"
                                self.sock.send(responce.encode())

                                self.sock.send(responce.encode())
                                #print("here bitch")



                       # if (self.keep_alive and self.sock.gettimeout() == None):
                            #print("kept alive\n\n\n\n")
                          #  self.sock.settimeout(5)

            else:
                #print("Client closed connection: {}".format(peer_name))
                break
        #print("out loop")





