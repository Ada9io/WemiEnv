module.exports = {
    // 连接Socket服务端
    connectSocket(server_url){
        wx.connectSocket({
          url: server_url
        })
        this.openSocket()
    },
    //打开socket通道
    openSocket() {
        wx.onSocketOpen(() => {
          console.log('WebSocket is connected')
          this.setData({socketStatus:true})
        })
        wx.onSocketClose(() => {
          console.log('WebSocket is not connected')
          this.setData({socketStatus:false})
        })
        wx.onSocketError(error => {
          console.error('ERROR', JSON.stringify(error))
          // this.setData({
          //   loading: false
          // })
        })
        // 监听服务器推送消息，并对消息做出回应
        wx.onSocketMessage(message => {
            // 收到服务器传来的action时执行动作，并返回下一次的观测状态
            var msg = JSON.parse(message.data);
            var ssx = msg['action'];
            var restart=msg['restart'];
            console.log(ssx);
            if (restart == true ) {
                // 改变状态并发送新状态
                this.reset();
                this.socket_send();
                }
            if (ssx == 0) {
                // 根据接收到的动作编号进行操作
                var reward = this.step(0);
                this.socket_send(reward);
            }
        })
      },
    // 发送游戏数据
    socket_send(reward){
        let msg={
            done: this.data.modalHidden,
            reward: reward,
            obs: this.data.numbers,
           }
        wx.sendSocketMessage({
          data: JSON.stringify(msg),
          success:(res)=>{
            // console.log("", res)
            },
            fail(res) {
            console.log("Fail to send.", res)
            }
        })
    },
}