const WebSocket = require('ws');

const ws = new WebSocket('ws://192.168.0.46:8080/websocket');

var devId = "084vvm0eo0000000000009e9"
ws.on('open', function open() {
  auth = {"deviceId": devId }
  ws.send(JSON.stringify(auth));
});

ws.on('message', function incoming(data) {
  console.log(data);
});

function sendHello() {
  ws.send('hello from devId: ' + devId);
}

setInterval(sendHello, 10000)
