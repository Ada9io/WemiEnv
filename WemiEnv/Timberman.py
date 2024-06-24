import time
import gym
from gym import spaces
import numpy as np
import json
from websocket_server import WebsocketServer
import logging
import threading
# gym.Env是gym的环境基类,自定义的环境就是根据自己的需要重写其中的方法；
# 必须要重写的方法有:
# __init__()：构造函数
# reset()：初始化环境
# step()：环境动作,即环境对agent的反馈
# render()：如果要进行可视化则实现 (可选)
class Timberman(gym.Env):
    def __init__(self):
        # 动作空间
        self.action_space = spaces.Discrete(2)
        self.action_meanings = "action =0右砍; =1左砍; =3重新开始"
        # 状态空间， 28（行）*22（列）的矩阵，降维成一维
        self.observation_space = spaces.Box(low=0, high=10, shape=(616, ), dtype=np.int32)
        # 当前观测状态
        self.cur_obs = None
        # 服务端创建
        self.conn = Connection()
        self.conn.create_server()
        # 等到客户端连接
        self.conn.waiting_client()

    def reset(self):
        message = {
            "action": 5,
            "restart": True,
        }
        message = json.dumps(message)
        self.conn.send_message(message)
        print("重新开始")

        obs = None
        # 循环直到接收到新的观测状态
        while obs == None:
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                obs = data["obs"]
        # 对接收到的2*2矩阵进行降维处理
        obs = list(np.array(obs).ravel())
        return obs

    def step(self, action):
        message = {
            "action": int(action),
            "restart": False,
        }
        message = json.dumps(message)
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
        print("obs: ", obs)
        # 对接收到的2*2矩阵进行降维处理
        obs = list(np.array(obs).ravel())
        return obs, reward, done, None


class Connection():
    def __init__(self):
        self.latest_msg = None
        self.server = None

    def create_server(self, host='0.0.0.0', port=7891, loglevel=logging.INFO):
        # 当有客户端连接时执行的代码
        def new_client(client, server):
            print("客户端已连接")
        # 当有客户端断开连接时执行的代码
        def left_client(client, server):
            print("客户端已断开")
        # 接收到新的客户端消息时执行的代码
        def new_received(client, server, msg):
            print(msg)
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
            print("服务端未创建")
            return
        if(len(self.server.clients)==0):
            print("发送消息失败，当前无客户端连接")
            return
        else:
            self.server.send_message(self.server.clients[0], msg_send)
            # print("发送消息成功")
            return
    # 接收最近传来的消息，如果接收成功，则把最近传来的消息清空，防止重复接收
    def recv_message(self):
        if self.server is None:
            print("服务端未创建")
            return
        if self.latest_msg is None:
            # print("最近无消息接收")
            return None
        else:
            msg = self.latest_msg
            self.latest_msg = None
            return msg

    def waiting_client(self):
        if self.server is None:
            print("服务端未创建")
            return
        print("等待客户端连接...")
        while(len(self.server.clients)==0):
            pass
        return


if __name__ == '__main__':
    # 测试
    env = CrazyTree()
    env.reset()
    env.step(0)
    time.sleep(1)
    env.step(0)
    time.sleep(1)
    env.step(0)
    time.sleep(1)
    env.step(0)
    time.sleep(1)
    env.reset()