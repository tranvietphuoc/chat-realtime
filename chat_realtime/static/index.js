document.addEventListener('DOMContentLoaded', () => {
  // connect to the Socket.IO server
  // the connection URL has following format, relative to the current page
  let socket = io();

  // event handler for new connections
  // the callback function is invoked when a connection with the server is established.
  socket.on('connect', () => {
    socket.emit('my_event', { data: "I'm connected." });
  });

  // event handler for server sent data
  // the callback function is invoked whenever the server emit data
  // to the client, the data is displayed in the "Receive" section of the page
  socket.on('my_response', (msg, cb) => {
    let log = document.querySelector('#log');
    let div = document.createElement('div');
    div.textContent = 'Receive #' + msg.count + ': ' + msg.data;
    log.appendChild(div);
    // log.append('<br>' + div);
    if (cb) cb();
  });
  // interval function that tests message latency by sending a "ping" message.
  // the server then response with a "pong" message and the round trip time is measured.
  let pingPongTimes = [];
  let startTime;
  window.setInterval(() => {
    let transport = document.querySelector('#transport');
    startTime = new Date().getTime();
    transport.textContent = socket.io.engine.transport.name;
    socket.emit('my_ping');
  }, 1000);

  // handler for the 'pong message'. when the pong is receive, the time from the ping
  // is stored, and the average of the last 30 samples is average and displayed
  socket.on('my_pong', () => {
    let pingPong = document.querySelector('#ping-pong');
    let latency = new Date().getTime() - startTime;
    pingPongTimes.push(latency);
    pingPongTimes = pingPongTimes.slice(-30); // keep last 30 samples
    let sum = 0;
    for (let i = 0; i < pingPongTimes.length; i++) {
      sum += pingPongTimes[i];
    }
    pingPong.textContent = Math.round(sum / pingPongTimes.length) / 10;
  });

  // handler for the different forms in the page
  document.querySelector('#emit').addEventListener('submit', (event) => {
    let emitData = document.querySelector('#emit-data');
    socket.emit('my_event', { data: emitData.value });
    return false;
  });

  document.querySelector('#broadcast').addEventListener('submit', (event) => {
    let broadcastData = document.querySelector('#broadcast-data');
    socket.emit('my_broadcast_event', { data: broadcastData.value });
    return false;
  });

  document.querySelector('#join').addEventListener('submit', (event) => {
    let joinRoom = document.querySelector('#join-room');
    socket.emit('join', { room: joinRoom.value });
    return false;
  });

  document.querySelector('#leave').addEventListener('submit', (event) => {
    let leaveRoom = document.querySelector('#leave-room');
    socket.emit('leave', { room: leaveRoom.value });
    return false;
  });

  document.querySelector('#send-room').addEventListener('submit', (event) => {
    let roomName = document.querySelector('#room-name');
    let roomData = document.querySelector('#room-data');
    socket.emit('my_room_event', {
      room: roomName.value,
      data: roomData.value,
    });
    return false;
  });

  document.querySelector('#close').addEventListener('submit', (event) => {
    socket.emit('close_room', {
      room: document.querySelector('#close-room').value,
    });
    return false;
  });

  document.querySelector('#disconnect').addEventListener('submit', (event) => {
    socket.emit('disconnect_request');
    return false;
  });
});
