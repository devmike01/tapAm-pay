 const roomName = JSON.parse(document.getElementById('session-room-name').textContent);

const sessionSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/session/'
    + roomName
    + '/'
);

sessionSocket.onmessage = function(e){
    const data = JSON.parse(e.data);
    document.getElementById("timer").innerHTML = data.message;
};
sessionSocket.onclose = function(e){
    console.error('Chat socket closed unexpected');
};

document.querySelector('#session-pause').onclick = function(e){
    const message = "[PAUSE]";
    sessionSocket.send(JSON.stringify({
'cmd': message
    }));

}

document.querySelector('#session-start').onclick = function(e){
    const message = "[START]";
    sessionSocket.send(JSON.stringify({
'cmd': message
    }));
}