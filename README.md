# WemiEnv - WeChat Mini Game Reinforcement Learning Environment

WemiEnv is a reinforcement learning environment built for WeChat mini-games. It provides an interface for RL agents to interact with WeChat mini-games, allowing them to receive observation results and send actions. The interface is built on Websocket network communication. Currently, WemiEnv supports four WeChat mini-game environments: Game2048, Flappybird, BottleJump, and Planewar. Users can also customize and create their own WeChat mini-game environments through the interfaces provided by WemiEnv.

We have published an accompanying paper outlining the motivation behind establishing a reinforcement learning platform for WeChat mini-games and presenting some preliminary research results using this environment.

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

WemiEnv

|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|create_env()|Create a WechatRL environment|Environment name|Environment object|
|env.step()|Send the next action to the simulator|message|Next observation|
|env.reset()|Reset the simulator environment|None|Next observation|

WebSocket_Server(python interact)

|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|create_server()|Create a Websocket server|Optional: host, port|None|
|send_message()|Send message to the client|message|None|
|recv_message()|Receives the most recent message from the client|None|message|
|waiting_client()|Wait for the client to connect|None|None|

WebSocket_Client(javascript interact)
|Method|Description|Takes|Gives|
|:---:|:---:|:---:|:---:|
|connectSocket()|Create a Websocket client and connect to a websocket server|server_url|None|
|socket_send()|Send message to the server|message|None|
|wx.onSocketMessage()|Defines the function that is executed when an action is received|None|None|