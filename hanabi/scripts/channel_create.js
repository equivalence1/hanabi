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
    document.getElementById("last").innerHTML += "Channel opened!";
}

function deserialize(str, arg_name) {
    var start = str.indexOf(arg_name, str.indexOf("?")) + arg_name.length + 1;
    var end = str.indexOf("&", start);

    if (end == -1) end = str.length - 1;

    return str.substr(start, end - start);
}

function onMessage(msg) {
    document.getElementById("last").innerHTML += "<br> msg: " + msg.data;

    if (msg.data.indexOf("joined") === 0) {
        game_name = deserialize(msg.data, "game_name");
        document.getElementById("last").innerHTML = msg.data;
        display_chat_room();
    }

    if (msg.data.indexOf("new_message") === 0) {
        var new_message = deserialize(msg.data, "message");
        var from_id = deserialize(msg.data, "fromid");
        add_message(from_id, new_message);
    }

    if (msg.data.indexOf("created") === 0) {
        display_chat_room();
        document.getElementById("start").style.display = "";
    }
}

function onError(err) {
    alert(err);
}

function onClose() {
    document.getElementById("last").innerHTML += "Channel closed!";
}
