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
