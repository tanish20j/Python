import socket
import os,sys
import threading
class Client:
    def __init__(self,name,status):
        self.s = socket.socket()     #create socket
        self.host = '192.168.1.3'     #(my pc) server's ip address
        self.port = 1234             #can be anything till 10000.Servers port number
        self.s.connect((self.host, self.port)) #connects to server
        self.clients = {}
        self.status = status
        self.my_username = name
        self.username = self.my_username.encode('utf-8')
        self.username_header = f"{len(self.username):<10}".encode('utf-8')
        self.s.send(self.username_header + self.username+self.status.encode('utf-8'))
    def send_commands(self,sms):    #method used to send data to server
        self.cmd = sms
        if self.cmd == 'quit':
            self.s.send(str.encode(self.cmd))  #this sends data of 'cmd' to server by encoding it in binary
            self.s.shutdown(socket.SHUT_RDWR) #used to close connection
            self.s.close()                    #used to close ocket
            sys.exit()                      #closes application
        if len(str.encode(self.cmd)) > 0:
            self.s.send(f"{len(self.cmd):<10}".encode('utf-8')+str.encode(self.cmd)+self.status.encode('utf-8'))      #this sends data of 'cmd' to server by encoding it in binary
    def get_response(self):
        while True:
            self.i=1
            type= self.s.recv(6)
            if type.decode('utf-8') == 'messag':
                message_header = self.s.recv(10)
                if not len(message_header):
                    return False
                client_length = int(message_header.decode('utf-8').strip())
                self.client_name = str(self.s.recv(client_length), "utf-8")  #this is used to recevie data from server and converts binary data to string
                message_header = self.s.recv(10)
                if not len(message_header):
                    return False
                message_length = int(message_header.decode('utf-8').strip())
                self.client_response = str(self.s.recv(message_length), "utf-8")
                if not self.client_response:                                 #if no data recived
                    sys.exit(0)
                print(f"{self.client_name} : {self.client_response} ")
                self.i = 0
            elif type.decode('utf-8') == 'update':

                message_header = self.s.recv(10)
                if not len(message_header):
                    return False
                no_of_client = int(message_header.decode('utf-8').strip())
                for i in range(0, no_of_client):
                    message_header = self.s.recv(10)
                    if not len(message_header):
                        return False
                    client_length = int(message_header.decode('utf-8').strip())
                    client_name = str(self.s.recv(client_length), "utf-8")
                    status = str(self.s.recv(7), "utf-8")
                    self.clients[self.client_name] = status
                print(self.clients)

    def thread(self):
        #t1 = threading.Thread(target=self.send_commands)  #thread t1(sending data)
        t2 = threading.Thread(target=self.get_response)   #thread t2(recieving data)
        #t1.start()                                              #first thread starts(sending data)
        t2.start()                                              #second thread starts(recieving data)
        #t1.join()                                               #t1 ends
        t2.join()                                               #t2 ends
        self.s.close()                                               #socket closed
if __name__== "__main__":
    start=Client()
    start.thread()
