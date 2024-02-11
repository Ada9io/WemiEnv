import time
import gym
from gym import spaces
import numpy as np
import json
from websocket_server import WebsocketServer
import logging
import threading
class BottleJumpEnv():
    def __init__(self):
        # 动作空间，跳一跳的动作是按压时长，为大于0的实数
        self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)
        # self.action_space = spaces.Discrete(2000)
        # 状态空间，当状态空间有多个向量时，会把多个向量看作多个样例，返回对应的action列表（返回numpy类型的对象）
        self.observation_space = spaces.Box(low=-1, high=1, shape=(1, ), dtype=np.float32)
        # 当前观测状态
        self.cur_obs = None
        # 服务端创建
        self.conn = Connection()
        self.conn.create_server()
        # 等到客户端连接
        self.conn.waiting_client()

    def reset(self):
        message = {
            "action": -1,
            "restart": True,
        }
        message = json.dumps(message)
        time.sleep(2)
        self.conn.send_message(message)
        # print("重新开始")
        
        obs = None
        # 循环直到接收到新的观测状态
        while obs == None:
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                obs = data["obs"]
                # gui yi hua
                obs[0] /= 40
        # 对接收到的2*2矩阵进行降维处理
        obs = list(np.array(obs).ravel())
        return obs

    def step(self, action):
        message = {
            "action": int(action[0]*400 + 700),
            # "action": int(action),
            "restart": False,
        }
        # print("action: ", action)
        message = json.dumps(message)
        time.sleep(1)
        self.conn.send_message(message)
        # 接收小程序数据
        obs = None
        # 循环直到接收到新的观测状态
        while obs == None:
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                obs = data["obs"]
                reward = data["reward"]
                done = data["done"]
                obs[0] /= 40
        # 对接收到的2*2矩阵进行降维处理
        obs = list(np.array(obs).ravel())
        # iprint(obs, reward, done)
        return obs, reward, done, None


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
    # 测试
    env = BottleJumpEnv()
    env.reset()
    time.sleep(1)
    env.reset()
    time.sleep(1)
    env.step(0)
    time.sleep(1)
    env.step(0)
    time.sleep(1)
    env.step(0)
