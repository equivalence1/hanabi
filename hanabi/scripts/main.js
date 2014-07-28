function create_game() {
    var game_name = document.getElementById("game_name").value.toString();
    var game_password = document.getElementById("password").value.toString();

    sendMessage("/game_create", "game_name=" + game_name + "&password=" + game_password)
}

function add_to_list(name) {
    var new_game = document.createElement("div");
    new_game.setAttribute("class", "game_div");
    new_game.id = "room_name=" + name;
    new_game.name = name;
    
    var game_name = document.createElement("div");
    game_name.setAttribute("class", "game_name");
    game_name.innerHTML = name;

    var join_button = document.createElement("div");
    join_button.setAttribute("class", "join_button");
    join_button.innerHTML = "join";
    join_button.setAttribute("room_name", name);
    join_button.onclick = join_room;

    new_game.appendChild(game_name);
    new_game.appendChild(join_button);

    var room_list = document.getElementById("game_list");
    room_list.appendChild(new_game);
}

function join_room() {
    var game_password = prompt("Enter password");
    sendMessage("/join_game", "game_name=" + this.getAttribute("room_name") + "&user_id=" + user_id + "&game_password=" + game_password);

    display_chat_room();
}

function display_chat_room() {
    document.getElementById("main_content").style.display = 'none';
    document.getElementById("chat_room").style.display = '';
}

function submit() {
    sendMessage("/send_chat_message", "user_id=" + user_id + "&message=" + document.getElementById("message").value + "&game_name=" + game_name);
    document.getElementById("message").value = "";
}