var game_name;

function create_game() {
    game_name = document.getElementById("game_name").value.toString();
    var game_password = document.getElementById("password").value.toString();

    sendMessage("/game_create", "game_name=" + game_name + "&password=" + game_password + "&user_id=" + user_id + "&max_user_count=4");
}

function join_room() {
    var game_password = prompt("Enter password");
    sendMessage("/join_game", "user_id=" + user_id + "&game_password=" + game_password + "&game_name=" + this.getAttribute("room_name"));
}

function start_game() {
    sendMessage("/start_game", "user_id=" + user_id + "&game_name=" + game_name);
}

function submit() {
    sendMessage("/send_chat_message", "user_id=" + user_id + "&game_name=" + game_name + "&message=" + document.getElementById("message").value);
    document.getElementById("message").value = "";
}

function hide_all() {
    document.getElementById("main_content").style.display = "none";
    document.getElementById("chat_room").style.display = "none";
    document.getElementById("start").style.display = "none";
    document.getElementById("game_table").style.display = "none";
}

function display_chat_room() {
    document.getElementById("chat_room").style.display = "";
}

function display_start_game_button() {
    document.getElementById("start").style.display = "";
}

function display_game_table() {
    document.getElementById("game_table").style.display = "";
}

function add_message(from_id, msg) {
    var new_message = document.createElement("div");
    new_message.setAttribute("class", "message_div");

    var from_user = document.createElement("div");
    from_user.class = "msg_user";
    from_user.innerHTML = from_id + ":";
    var content = document.createElement("div");
    content.class = "msg_content";
    content.innerHTML = msg;

    new_message.appendChild(from_user);
    new_message.appendChild(content);

    var chat = document.getElementById("chat");
    chat.appendChild(new_message);
}

function add_to_list(name, fill, locked) {
    var new_game = document.createElement("div");
    new_game.setAttribute("class", "game_div");
    new_game.id = "room_name=" + name;
    new_game.name = name;

    var game_name = document.createElement("div");
    game_name.setAttribute("class", "game_name");
    game_name.innerHTML = name + "    " + fill;

    var join_button = document.createElement("div");
    join_button.setAttribute("class", "join_button");
    join_button.innerHTML = "join";
    join_button.setAttribute("room_name", name);
    join_button.onclick = join_room;
        join_button.setAttribute("data-toggle", "tooltip");
        join_button.setAttribute("data-placement", "top");
        join_button.setAttribute("title", "This room has password");

    new_game.appendChild(game_name);
    new_game.appendChild(join_button);

    if (locked.toString() === "True") {
        var span = document.createElement("span");
        span.setAttribute("class", "glyphicon glyphicon-lock");
        span.setAttribute("style", "float: right; margin-top: 5px");
        span.setAttribute("data-toggle", "tooltip");
        span.setAttribute("data-placement", "top");
        span.setAttribute("title", "This room has password");

        new_game.appendChild(span);
    }        

    var room_list = document.getElementById("game_list");
    room_list.appendChild(new_game);
}

function update_online_list(count, user_str) {
    document.getElementById("online_list").innerHTML = "Online(" + count + "):<br>" + user_str;
}

function refresh() {
    var game_list = document.getElementById("game_list");

    while (game_list.firstChild) {
        game_list.removeChild(game_list.firstChild);
    }

    sendMessage("/game_list_refresh", "user_id=" + user_id);
}
