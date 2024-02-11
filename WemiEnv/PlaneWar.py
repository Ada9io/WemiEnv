import logging
import math
from typing_extensions import *
import cv2
from socket import *
import ast
import time
import numpy as np
import json
from websocket_server import WebsocketServer
class PlaneWarEnv():
    screen_width = 375
    screen_height = 625
    plain_width = 165
    plain_height = 265
    def __init__(self):
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        # self.action_space.high = np.array([4])
        # self.action_space.low = np.array([0])
        self.action_meanings = "The angle at which the plane moves."
        self.obsSize = 26
        self.obsShape = (self.obsSize)
        # self.obsShape = (1,self.obsSize)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(self.obsSize,), dtype=np.float32)  # 状态空间
        # 其他成员
        self.conn = Connection()
        self.conn.create_server()
        # 等到客户端连接
        self.conn.waiting_client()

    def reset(self):
        np.random.seed(0)
        message = {
            "action": 0,
            "restart": True,
            # "restart": "true",
        }
        message = json.dumps(message)
        self.conn.send_message(message)
        # print("重新开始游戏")

        obs = None
        npobs = []
        while obs == None:
            # data = self.tcp_recv()
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                plains = data["plains"]
                player = data["player"]
                obs = []
                obs.extend([(2 * player["x"] / 375) - 1, (2 * player["y"] / 625) - 1])
                for plain in plains:
                    obs.extend([(2*plain["type"] / 3)-1, (2*plain["x"] / 375)-1, (2*plain["y"] / 625)-1])
                lenobs = len(obs)
                npobs = np.array(obs)
                npobs = np.pad(npobs, (0, self.obsSize - lenobs), 'constant', constant_values=(0))  # 飞机数量不到8架则填充0
                # print(self.__class__.__name__, "step return obs shape", npobs.shape,npobs)
                npobs = npobs.reshape(self.obsShape)
                npobs = list(np.array(npobs).ravel())
        # print(self.__class__.__name__, "step return obs shape",npobs)
        return npobs

    def step(self, action):
        message = {
            "action": float(action[0]),
            "restart": False,
        }
        # print(message)
        # print(self.__class__.__name__, "step tcp_send 动作给微信小程序:", message)
        # 发送初始动作和重启小游戏命令给微信小程序
        # message = json.dumps(message, ensure_ascii=False)
        # self.tcp_send(message)
        message = json.dumps(message)
        self.conn.send_message(message)
        # 接受来自小程序的数据
        obs = None
        while obs == None:
            # data = self.tcp_recv()
            data = self.conn.recv_message()
            # 循环直到接收到data
            if data != None:
                data = json.loads(data)
                # t = time.time()
                # t = (int(round(t * 1000)))
                # print("recive time :",t)
                # st = data['time']
                # print("send time:",st)
                # print(t-st)
                reward = data["reward"]  #
                terminal = data["status"]  #
                player = data["player"]
                plains = data["plains"]
                obs = []
                obs.extend([(2*player["x"] / 375)-1, (2*player["y"] / 625)-1])
                for plain in plains:
                    obs.extend([(2*plain["type"] / 3)-1,  (2*plain["x"] / 375)-1, (2*plain["y"] / 625)-1])
                lenobs = len(obs)
                npobs = np.array(obs)
                npobs = np.pad(npobs, (0, self.obsSize - lenobs), 'constant', constant_values=(-1))  # 飞机数量不到8架则填充-1
                # print(self.__class__.__name__, "step return obs shape", npobs.shape, npobs)
                npobs = npobs.reshape(self.obsShape)
                npobs = list(np.array(npobs).ravel())

                # print(self.__class__.__name__, "step tcp_recv 接受来自小程序的数据:", npobs)
        return npobs, reward, terminal, None


class Connection():
    def __init__(self):
        self.latest_msg = None
        self.server = None

    def create_server(self, host='0.0.0.0', port=7891, loglevel=logging.INFO):
        # 当有客户端连接时执行的代码
        def new_client(client, server):
            print("The client connects successfully.")
        # 当有客户端断开连接时执行的代码
        def left_client(client, server):
            print("The client disconnects.")
        # 接收到新的客户端消息时执行的代码
        def new_received(client, server, msg):
            # print(msg)
            # 收到新消息时，更新最近收到的消息
            self.latest_msg = msg

        # 创建一个websocket服务端server
        self.server = WebsocketServer(host, port, loglevel)
        # 设定有新客户端连接时的回调函数
        self.server.set_fn_new_client(new_client)
        # 设定有客户端断开时的回调函数
        self.server.set_fn_client_left(left_client)
        # 设定服务端接收到客户端消息时的回调函数
        self.server.set_fn_message_received(new_received)
        # 创建新线程用于持续建立连接
        self.server.run_forever(threaded=True)

    def send_message(self, msg_send):
        if self.server is None:
            print("The server is not created.")
            return
        if(len(self.server.clients)==0):
            print("Failed to send a message, there is no client connection.")
            return
        else:
            self.server.send_message(self.server.clients[0], msg_send)
            # print("The message was sent successfully.")
            return
    # 接收最近传来的消息，如果接收成功，则把最近传来的消息清空，防止重复接收
    def recv_message(self):
        if self.server is None:
            print("The server is not created.")
            return
        if self.latest_msg is None:
            # print("No messages have been received recently.")
            return None
        else:
            msg = self.latest_msg
            self.latest_msg = None
            return msg

    def waiting_client(self):
        if self.server is None:
            print("The server is not created.")
            return
        print("Waiting for the client to connect.")
        while(len(self.server.clients)==0):
            pass
        return

if __name__ == '__main__':
    env = PlaneWarEnv()
    # Test
    while(True):
        obs, reward, terminal, _ = env.step([0.8])
        print(obs)
        print(reward)
        print(terminal)
        time.sleep(0.2)
