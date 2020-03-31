import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager,Screen
import threading
import sys
import client as cl

class Stat():
    def __init__(self):
        self.name = ""
        self.status = ""
back=Stat()
class WindowManager(ScreenManager):
    pass

class Second(Screen):
    def send(self):
        print(self.ids.sms.text)
        self.start.send_commands(self.ids.sms.text)
        self.ids.msglog.text = self.ids.msglog.text+"\n"+self.start.my_username+" : " + self.ids.sms.text
        self.ids.sms.text = ""

    def connect(self):
        self.start = cl.Client(back.name , back.status)
        threading.Thread(target=self.recive).start()
    def recive(self):
        while True:
            type = self.start.s.recv(6)
            if type.decode('utf-8') == 'messag':
                message_header = self.start.s.recv(10)
                if not len(message_header):
                    return False
                client_length = int(message_header.decode('utf-8').strip())
                client_name = str(self.start.s.recv(client_length), "utf-8")  # this is used to recevie data from server and converts binary data to string
                message_header = self.start.s.recv(10)
                if not len(message_header):
                    return False
                message_length = int(message_header.decode('utf-8').strip())
                client_response = str(self.start.s.recv(message_length), "utf-8")
                if not client_response:  # if no data recived
                    sys.exit(0)
                print(f"{client_name} : {client_response} ")
                self.ids.msglog.text = self.ids.msglog.text + "\n" + client_name + " : " + client_response
            elif type.decode('utf-8') == 'update':
                self.start.clients.clear()
                message_header = self.start.s.recv(10)
                if not len(message_header):
                    return False
                no_of_client = int(message_header.decode('utf-8').strip())
                for i in range(0, no_of_client):
                    message_header = self.start.s.recv(10)
                    if not len(message_header):
                        return False
                    client_length = int(message_header.decode('utf-8').strip())
                    client_name = str(self.start.s.recv(client_length), "utf-8")
                    status = str(self.start.s.recv(7), "utf-8")
                    self.start.clients[client_name] = status
                print(self.start.clients)
                self.ids.online.text =""
                for i in self.start.clients:
                    self.ids.online.text = self.ids.online.text +"\n" + str(i)

class Third(Screen):
    def op1(self):
        back.name="Dipti Ma'am"
        back.status="Teacher"
    def op2(self):
        back.name = "Kiran Ma'am"
        back.status = "Teacher"
    def op3(self):
        back.name = "Dhanalakshmi Ma'am"
        back.status = "Teacher"

class Fourth(Screen):
    def btn(self):
        print(self.ids.studentname.text)
        back.name = self.ids.studentname.text
        back.status = "Student"








class First(Screen):
    pass
# class MyGrid(Widget):
#     # msg = ObjectProperty(None)                            #
#     # msg1 =ObjectProperty(None)                             #
#     # def send(self):
#     #     print(self.msg.text, self.msg1.text)                #
#     #     self.msg.text=""                                    #
#     #     self.msg1.text=""                                   #
#
#     pass


kv=Builder.load_file("ty.kv")

class TyApp(App):
    def build(self):
        return kv

TyApp().run()
