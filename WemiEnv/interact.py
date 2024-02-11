from websocket_server import WebsocketServer
import logging

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

if __name__ == "__main__":
    conn = Connection()
    conn.create_server()
    conn.waiting_client()
    # 测试程序保持进程进行
    while True:
        pass


