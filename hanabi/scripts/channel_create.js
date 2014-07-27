var socket = channel.open();
socket.onopen = onOpened;
socket.onmessage = onMessage;
socket.onerror = onError;
socket.onclose = onClose;

function sendMessage(path, opt_param) {
    path += '?g=' + "my_game";
    if (opt_param) {
        path += '&' + opt_param;
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', path, true);
    xhr.send();
}

function onOpened() {
    alert("Channel opened!");
}

function onMessage(msg) {
    alert(msg.data);
}

function onError(err) {
    alert(err);
}

function onClose() {
    alert("Channel closed!");
}
