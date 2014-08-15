var socket = channel.open();
socket.onopen = onOpened;
socket.onmessage = onMessage;
socket.onerror = onError;
socket.onclose = onClose;

function sendMessage(path, opt_param) {
    path += '?g=' + "g";
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

function onError(err) {
    alert(err);
}

function onClose() {
    document.getElementById("last").innerHTML += "Channel closed!";
}

function deserialize(str, arg_name) {
    var start = str.indexOf(arg_name, str.indexOf("?")) + arg_name.length + 1;
    var end = str.indexOf("&", start);

    if (end == -1) end = str.length;

    return str.substr(start, end - start);
}

function onMessage(msg) {
    document.getElementById("last").innerHTML += "<br> msg: " + msg.data;

    if (msg.data.indexOf("joined") === 0) {
        game_name = deserialize(msg.data, "game_name");
        document.getElementById("last").innerHTML = msg.data;
        var users_count = deserialize(msg.data, "users_count");
        var users_str = deserialize(msg.data, "users_list");
        update_online_list(users_count, users_str);
        hide_all();
        display_chat_room();
    }

    if (msg.data.indexOf("new_message") === 0) {
        var new_message = deserialize(msg.data, "message");
        var from_id = deserialize(msg.data, "from_id");
        add_message(from_id, new_message);
    }

    if (msg.data.indexOf("created") === 0) {
        var users_count = deserialize(msg.data, "users_count");
        var users_str = deserialize(msg.data, "users_list");
        update_online_list(users_count, users_str);
        hide_all();
        display_chat_room();
        display_start_game_button();
    }

    if (msg.data.indexOf("update_online") == 0) {
        var users_count = deserialize(msg.data, "users_count");
        var users_str = deserialize(msg.data, "users_list");
        update_online_list(users_count, users_str);
    }

    if (msg.data.indexOf("start_game") == 0) {
        hide_all();

        game_state.life = deserialize(msg.data, "life");
        game_state.hint = deserialize(msg.data, "hint");
        game_state.whose_move = deserialize(msg.data, "whose_move");
        game_state.my_position = parseInt(deserialize(msg.data, "your_position"));
        game_state.users_count = deserialize(msg.data, "users_count");
        game_state.deck_size = deserialize(msg.data, "deck_size");

        game_state.hand = [];
        for (i = 0; i < game_state.users_count; i++) {
            game_state.hand[i] = [];
            if (game_state.my_position != i) {
                var cards_str = deserialize(msg.data, "user" + i + "cards");
                for (var j = 0; j < cards_str.length / 2; j++) {
                    game_state.hand[i][j] = {};
                    game_state.hand[i][j].color = parseInt(cards_str[j * 2]);
                    game_state.hand[i][j].value = parseInt(cards_str[j * 2 + 1]);
                }
            }
        }

        game_state.solitaire = [];
        game_state.scores = 0;
        var solitaire_str = deserialize(msg.data, "solitaire");
        for (i = 0; i < solitaire_str.length / 2; i++) {
            game_state.solitaire[i] = {};
            game_state.solitaire[i].color = parseInt(solitaire_str[i * 2]);
            game_state.solitaire[i].value = parseInt(solitaire_str[i * 2 + 1]);
            game_state.scores += game_state.solitaire[i].value;
        }

        game_state.junk = [];
        var junk_str = deserialize(msg.data, "junk");
        for (i = 0; i < junk_str.length / 2; i++) {
            game_state.junk[i] = {};
            game_state.junk[i].color = parseInt(junk_str[i * 2]);
            game_state.junk[i].value = parseInt(junk_str[i * 2 + 1]);
        }

        display_game_table();
        update_game_table();
    }

    if (msg.data.indexOf("hint") == 0) {
        hint = {};
        hint.from_player = deserialize(msg.data, "from_player");
        hint.to_player = deserialize(msg.data, "to_player");
        hint.hint_type = deserialize(msg.data, "type");
        hint.card_ids = deserialize(msg.data, "card_ids");
        if (hint.hint_type == "color")
            hint.hinted_color = deserialize(msg.data, "hinted_color");
        else
            hint.hinted_value = deserialize(msg.data, "hinted_value");
    }

    if (msg.data.indexOf("add_game_to_list") == 0) {
        var game_list = document.getElementById("game_list");

        while (game_list.firstChild) {
            game_list.removeChild(game_list.firstChild);
        }

        var N = deserialize(msg.data, "num");
        for (i = 0; i < N; i++) {
            var game_name_i = deserialize(msg.data, "game_name" + i);
            var users_count = deserialize(msg.data, "users_count" + i);
            var max_users_count = deserialize(msg.data, "max_users_count" + i);
            var locked = deserialize(msg.data, "locked" + i);
            add_to_list(game_name_i, users_count + "/" + max_users_count, locked);
        }
    }
}
