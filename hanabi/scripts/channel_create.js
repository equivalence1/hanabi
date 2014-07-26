var socket = channel.open();
socket.onopen = onOpened;
socket.onmessage = onMessage;
socket.onerror = onError;
socket.onclose = onClose;

sendMessage = function(path, opt_param) {
  path += '?g=' + "my_game";
  if (opt_param) {
    path += '&' + opt_param;
  }
  var xhr = new XMLHttpRequest();
  xhr.open('POST', path, true);
  xhr.send();
};

function onOpened() {
    alert("Channel opened!");
    sendMessage("/test", "data=123");
    alert("Sended!");
}

function onMessage(msg) {
    alert(msg.data);
    document.getElementById("p").innerHTML += msg.data;
}

function onError(err) {
    alert(err);
}

function onClose() {
    alert("Channel closed!");
}

function send_message() {
    sendMessage("/test", "data=" + document.getElementById("content").value + "46");
    alert("Peremennaja!")
}