$( document ).ready(function() {
    document.getElementById("alert_modal_content").innerHTML = "";
    refresh();

    $("#alertModal").on("hidden.bs.modal", function() {
        document.getElementById("alert_modal_content").innerHTML = "";
        if (queue_to_show.length != 0)
            show_in_panel(queue_to_show.shift());
    });

    $("#alertModal").on("shown.bs.modal", function() {
        if ($("#pass_enter") != undefined)
            $("#pass_enter").focus();
    });

    nick = user_id;    
    document.getElementById("nick").innerHTML = user_id;
    
    if (tok == "None") {
        hide_all();
        document.getElementById("quota_error").style.display = "";
    }
});

function go_to_main() {
    hide_all();
    display_main_content();
    if (game_name != undefined) {
        sendMessage("/leave", "user_id=" + user_id + "&game_name=" + game_name);
        game_name = undefined;
        game_state = {};

        document.getElementById("game_name").value = "";
        document.getElementById("password").value = "";
        document.getElementById("chat").innerHTML = "";

        var game_list = document.getElementById("game_list");
        while (game_list.firstChild)
            game_list.removeChild(game_list.firstChild);
    }
    refresh();
}

function create_game() {
    game_name = document.getElementById("game_name").value.toString();
    var game_password = document.getElementById("password").value.toString();

    sendMessage("/game_create", "game_name=" + game_name + "&nick=" + nick + "&password=" + game_password + "&user_id=" + user_id + "&max_user_count=4");
}

function join_room() {
    var cont = document.getElementById("alert_modal_content");
    if (cont.innerHTML != "")
        return;
    if (this.getAttribute("locked") === "False") {
        sendMessage("/join_game", "user_id=" + user_id + "&nick=" + nick + "&game_password=" + "&game_name=" + this.getAttribute("room_name"));
        return;
    }
    var pan = document.createElement("div");
    pan.innerHTML = '<div class="panel-heading"><h4>Enter the password</h4></div>' +
    '<div class="panel-body">' +
    '<input type="text" class="form-control" placeholder="password" id="pass_enter" maxlength="20" size="20" style="width: 150px;">' +
    '<button type="button" class="btn btn-primary" style="float: right;" id="enter_btn" ' + 'room_name="' + this.getAttribute("room_name") + '">Enter</button>' +
    '<button type="button" class="btn btn-default" style="float: right;" id="cancel_btn">Cancel</button></div>';
    pan.setAttribute("class", "panel panel-primary pass_pan");
    pan.style.marginBottom = "0px";
    cont.appendChild(pan);
    document.getElementById("enter_btn").onclick = validate_pass;
    document.getElementById("cancel_btn").onclick = cancel_join;
    document.getElementById("pass_enter").setAttribute("onkeydown", "javascript:if(event.keyCode==13||event.keyCode==10)\
    {document.getElementById('enter_btn').click();}");
    $("#alertModal").modal("show");
}

function validate_pass() {
    var game_password = document.getElementById("pass_enter").value;
    $("#alertModal").modal("hide");
    sendMessage("/join_game", "user_id=" + user_id + "&nick=" + nick + "&game_password=" + game_password + "&game_name=" + this.getAttribute("room_name"));
}

function cancel_join() {
    $("#alertModal").modal("hide");
}

function start_game() {
    sendMessage("/start_game", "user_id=" + user_id + "&game_name=" + game_name);
}

function submit() {
    sendMessage("/send_chat_message", "user_id=" + user_id + "&nick=" + nick + "&game_name=" + game_name + "&message=" + document.getElementById("message").value);
    document.getElementById("message").value = "";
    document.getElementById("message").focus();
}

function hide_all() {
    document.getElementById("main_content").style.display = "none";
    document.getElementById("chat_room").style.display = "none";
    document.getElementById("start").style.display = "none";
    document.getElementById("game_table").style.display = "none";
    document.getElementById("new_nick").style.display = "none";
    document.getElementById("set_new_nick").style.display = "none";
}

function display_main_content() {
    document.getElementById("main_content").style.display = "";
    document.getElementById("new_nick").style.display = "";
    document.getElementById("set_new_nick").style.display = "";
}

function display_chat_room() {
    document.getElementById("message").value = "";
    document.getElementById("chat_room").style.display = "";
    document.getElementById("new_nick").style.display = "none";
    document.getElementById("set_new_nick").style.display = "none";
    document.getElementById("message").focus();
}

function display_start_game_button() {
    document.getElementById("start").style.display = "";
    document.getElementById("new_nick").style.display = "none";
    document.getElementById("set_new_nick").style.display = "none";
}

function display_game_table() {
    document.getElementById("game_table").style.display = "";
    document.getElementById("new_nick").style.display = "none";
    document.getElementById("set_new_nick").style.display = "none";
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

    var a = document.getElementsByClassName("message_div");
    a[a.length - 1].scrollIntoView();
}

function add_to_list(name, fill, locked) {
    var new_game = document.createElement("div");
    new_game.setAttribute("class", "game_div");
    new_game.id = "room_name=" + name;
    new_game.name = name;

    var game_name = document.createElement("div");
    game_name.setAttribute("class", "game_name");
    game_name.innerHTML = "<p> " + name + "    " + fill + " </p>";

    var join_button = document.createElement("button");
    join_button.setAttribute("class", "btn btn-info btn-xs join_button");
    join_button.innerHTML = "join";
    join_button.setAttribute("room_name", name);
    join_button.setAttribute("locked", locked.toString());
    join_button.onclick = join_room;

    new_game.appendChild(game_name);
    new_game.appendChild(join_button);

    if (locked.toString() === "True") {
        var span = document.createElement("span");
        span.setAttribute("class", "glyphicon glyphicon-lock");
        span.setAttribute("style", "float: right; margin-top: 5px; margin-right: 5px;");
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
    sendMessage("/game_list_refresh", "user_id=" + user_id);
}

function set_nick() {
    var new_nick = document.getElementById("new_nick").value;
    document.getElementById("new_nick").value = "";
    if (document.getElementById("main_content").style.display != "") {
        document.getElementById("nick").innerHTML = "You think u r so smart!?!?";
        return;        
    }
    if ($.trim(new_nick) != "") {
        nick = new_nick;
        document.getElementById("nick").innerHTML = nick;
    }
}
