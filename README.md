# WemiEnv - WeChat Mini Game Reinforcement Learning Environment

WemiEnv is a reinforcement learning environment built for WeChat mini-games. It provides an interface for RL agents to interact with WeChat mini-games, allowing them to receive observation results and send actions. The interface is built on Websocket network communication. Currently, WemiEnv supports six WeChat mini-game environments: Game 2048, Flappybird, Flip, Space Fighter, Snake and Timberman. Users can also customize and create their own WeChat mini-game environments through the interfaces provided by WemiEnv.

# Quick Start Guide
## Get WemiEnv
### From Source
you can install latest WemiEnv codebase from a local clone of the git repo:
```
$ git clone https://github.com/Ada9io/WemiEnv.git
```
## Get WeChat Mini Game Simulator
WemiEnv relies on the WeChat mini-game simulator, and we use the WeChat Developer Program as the default simulator for WemiEnv.
### Windows/MacOS
Windows/MacOS users can install the corresponding version of the WeChat mini-game simulator through the following website: 
https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html

## Get Wechat Mini Games

After installing the simulator, unzip and import the WeChat mini-game source code from the vchat_minigame folder.

If you wish to create a custom WeChat mini-game environment, you can directly import your desired WeChat mini-game source code and implement interaction using the interface functions provided by the API.

## Run an agent

After creating the WemiEnv environment, the agent will establish a server, waiting for the client to connect. At this point, starting the simulator will initiate the interaction channel between the agent and the simulator. When the terminal displays "The client connects successfully," it indicates the successful establishment of the channel. Users can then interact with the WemiEnv environment through the step() and reset() methods.

# Environment Details
WemiEnv uses WebSocket for network communication, and the server interface is by default created on the local port 7891. Users need to ensure that port 7891 is not occupied when establishing a connection. If needed, you can switch to a different port by using the following code:
```create_server(port=PORT_NUMBER)```
This allows users to customize the port number according to their preferences or to avoid conflicts with other applications using the default port.

# API

WemiEnv:

|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|create_env()|Create a WechatRL environment|Environment name|Environment object|
|env.step()|Send the next action to the simulator|message|Next observation|
|env.reset()|Reset the simulator environment|None|Next observation|

WebSocket_Server(writting in Python):

|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|create_server()|Create a Websocket server|Optional: host, port|None|
|send_message()|Send message to the client|message|None|
|recv_message()|Receives the most recent message from the client|None|message|
|waiting_client()|Wait for the client to connect|None|None|

WebSocket_Client(writting in Javascript)
|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|connectSocket()|Create a Websocket client and connect to a websocket server|server_url|None|
|socket_send()|Send message to the server|message|None|
|wx.onSocketMessage()|Defines the function that is executed when an action is received|None|None|

# Adding new games to WemiEnv

### Server
The server module is designed to exchange the information with the WeChat mini-program. It is written in python. To implement the server of WemiEnv, we need to first import the interact package from WemiEnv. Then, a new environment class needs to be implemented, with the default observation and action spaces defined and the communication server initialized based on WemiEnv. The interact packacge from WemiEnv is needed. An exemple code is shown as below：

```python
import interact
class MyEnv():
    def __init__(self):
        # Action space
        self.action_space = None
        # Observation space
        self.observation_space = None
        # Create a server
        self.conn = interact.Connection()
        self.conn.create_server()
        # Wait for the client to connect
        self.conn.waiting_client()
```

Finally, the ```reset()``` and ```step()``` function need to be implemented. Those two methods contain the information exchanging functions from the client:

```python
    def reset(self):
        # Send information
        message = {
            "action": None,
            "restart": True,
        }
        message = json.dumps(message)
        self.conn.send_message(message)
        # Receive information
        obs = None
        # Loop until receiving a message from the client
        while obs == None:
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                obs = data["obs"]
        obs = list(np.array(obs).ravel())
        return obs

    def step(self, action):
        # Send information
        message = {
            "action": action,
            "restart": False,
        }
        message = json.dumps(message)
        self.conn.send_message(message)
        # Receive information
        obs = None
        # Loop until receiving a message from the client
        while obs == None:
            data = self.conn.recv_message()
            if data != None:
                data = json.loads(data)
                obs = data["obs"]
                reward = data["reward"]
                done = data["done"]
        return obs, reward, done, None
```

### Client
The client module is built in the Wechat mini-program, and transfers information to the server. To implement the client, go-through the source code of the WeChat mini-game is necessary. 

First, import interact.js to the WeChat mini-program in an appropriate position:

```javascript
import * as interact from './interact.js';
```

Before building the communication module, users should go through the source code of the WeChat mini-game to find out the state, action, reward, and done signal to be transferred and define the appropriate data format for information exchange.  Then, users need to rewrite the ```openSocket() ```functions to connect the server:

```javascript
openSocket() {
        wx.onSocketOpen(() => {
          console.log('WebSocket is connected')
        })
        wx.onSocketClose(() => {
          console.log('WebSocket is not connected')
        })
        wx.onSocketError(error => {
          console.error('ERROR', JSON.stringify(error))
        })
        // Listen to and respond to messages sent by the server
        wx.onSocketMessage(message => {
            var msg = JSON.parse(message.data);
            var action = msg['action'];
            var restart=msg['restart'];
            if (restart == true ) {
                // Reset the game environment.
                this.reset();
                interact.socket_send(obs, reward, done);
            }
            // ===Major rewrite sections===
            if (action == 0) {
                this.step(0);
                interact.socket_send(obs, reward, done);
            }
            // ===Major rewrite sections===
        })
      },

```
User can define observation, reward, done signal from the source code of the mini-games, and transfering them with ```interact.socket_send(obs, reward, done)```. 

Finally, using the ```connectSocket()``` method to connect the client to the server. The default port for communication is 7891.

```javascript
interact.connectSocket('ws://localhost:7891')
```
