import threading
import socket
import json 
import time
import udp 
from config import seed
import random

#метод определния ip (локальный/за NAT)
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


class Node:
    seed = seed
    peers = {}
    myid = ""
    udp_socket = {}

    #принимает сообщения от подключенных клиентов:
    def rece(self):
        while True:
            data, addr = udp.recembase(self.udp_socket)
            action = json.loads(data) #то,что приходит на сервер peer

            if action['type'] == 'newpeer': #передает список пиров
                print("A new peer is coming")
                self.peers[action['data']] = addr  #DATA=myid
                udp.sendJS(self.udp_socket, addr, {
                "type": 'peers',
                "data": self.peers
                })         

            if action['type'] == 'peers':
                print("Received a bunch of peers")
                self.peers.update(action['data'])
                udp.broadcastJS(self.udp_socket, {
                    "type":"introduce",
                    "data": self.myid
                }, self.peers)

            if action['type'] == 'introduce':
                your_name= f'Пользователь {self.myid} присоединился'
                print(your_name)
                self.peers[action['data']]= addr   

            if action['type'] == 'input':
                print(action['data'])  

            if action['type'] == 'exit':
                if(self.myid == action['data']):
                    time.sleep(0.5) 
                    break
                value, key = self.peers.pop(action['data'])
                print(action['data'] + " is left.")
            
    def startpeer(self):
        udp.sendJS(self.udp_socket,self.seed,{
            "type": "newpeer",   #уведомляет сида о подключениии в сеть пира
            "data": self.myid
        })

    def send(self):
        while True: 
            msg_input = input("сообщение:")
            if not msg_input:
                continue
            if msg_input == "/exit":
                udp.broadcastJS(self.udp_socket, {
                    "type": "exit",
                    "data": self.myid
                }, self.peers)
                break
            if msg_input == "/friends":
                peers_in_chat=f'список участников: {self.peers}'
                print(peers_in_chat)
                continue
            l = msg_input.split()
            if l[-1] in self.peers.keys():
                toA = self.peers[l[-1]]
                s = ' '.join(l[:-1]) 
                udp.sendJS(self.udp_socket, toA, {
                    "type": "input",
                    "data": s
                })
            else:
                udp.broadcastJS(self.udp_socket, {
                    "type": "input",
                    "data": msg_input
                }, self.peers)
                continue 


def main():
    #определяем локальный ip адрес:
    my_ip=extract_ip()
    port = random.randint(10000,60000)    #Присвоение порта
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((my_ip, port))
    print(f'Адрес вашего сервера: {my_ip}:{port}')
    peer = Node() 
    peer.myid = input('Введите ваше имя: ') #Имя пользователя
    peer.udp_socket = udp_socket
    peer.startpeer() # Отправляет сообщение о новом подключенном пире
    t1 = threading.Thread(target=peer.rece, args=())
    t2 = threading.Thread(target=peer.send, args=())
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()          