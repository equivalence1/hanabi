card_amount_in_deck_by_value = [0, 3, 2, 2, 2, 1];
card_amount_in_hand_by_user_count = [0, 0, 5, 5, 4, 4];

color_by_number = ["undefined", "red", "green", "blue", "yellow", "white"];

function update_game_table() {
    var i = 0;

    var place = [];
    place[game_state.my_position] = "down_hand";
    if (game_state.users_count == 2) {
        place[((game_state.my_position + 1) % 2)] = "upper_hand";
    } else {
        for (i = 1; i < game_state.users_count; i++)
            place[(game_state.my_position + i) % game_state.users_count] = ["left_hand", "upper_hand", "right_hand"][i - 1];
    }

    for (i = 0; i < game_state.users_count; i++) {
        var hand = document.getElementById(place[i]);
        hand.innerHTML = "";
        for (var j = 0; j < card_amount_in_hand_by_user_count[game_state.users_count]; j++)
            add_card_to_hand(hand, game_state.hand[i][j], i, j);
    }

    var table = document.getElementById("table");

    var scores = document.createElement("div");
    scores.setAttribute("class", "score_message");
    scores.innerHTML = "Scores: " + game_state.solitaire.length.toString();
    table.appendChild(scores);

    for (i = 0; i < 3 - game_state.life; i++) {
        var dead_life = document.createElement("div");
        dead_life.setAttribute("class", "chip");
        dead_life.innerHTML = "<img src='images/dead_life.png'>";
        dead_life.style.left = (450 + 50 * i).toString() + "px";
        dead_life.style.top = "30px";
        table.appendChild(dead_life);
    }

    for (; i < 3; i++) {
        var alive_life = document.createElement("div");
        alive_life.setAttribute("class", "chip");
        alive_life.innerHTML = "<img src='images/alive_life.png'>";
        alive_life.style.left = (450 + 50 * i).toString() + "px";
        alive_life.style.top = "30px";
        table.appendChild(alive_life);
    }

    for (i = 0; i < 8 - game_state.hint; i++) {
        var dead_hint = document.createElement("div");
        dead_hint.setAttribute("class", "chip");
        dead_hint.innerHTML = "<img src='images/dead_hint.png'>"
        dead_hint.style.left = (500 + 50 * (i % 2)).toString() + "px";
        dead_hint.style.top = (80 + 50 * (i / 2 | 0)).toString() + "px";
        table.appendChild(dead_hint);
    }

    for (; i < 8; i++) {
        var alive_hint = document.createElement("div");
        alive_hint.setAttribute("class", "chip");
        alive_hint.innerHTML = "<img src='images/alive_hint.png'>"
        alive_hint.style.left = (500 + 50 * (i % 2)).toString() + "px";
        alive_hint.style.top = (80 + 50 * (i / 2 | 0)).toString() + "px";
        table.appendChild(alive_hint);
    }
}

function add_card_to_hand(hand, card, whoes_hand, card_id_in_hand) {
    var new_card = document.createElement("div");
    new_card.setAttribute("class", "card");
    new_card.setAttribute("whoes_hand", whoes_hand);
    new_card.setAttribute("card_id_in_hand", card_id_in_hand);
    new_card.setAttribute("id", whoes_hand * 10 + card_id_in_hand);

    if (card == undefined) {
        var span = document.createElement("span");
        span.setAttribute("class", "undefined_card");
        span.innerHTML = "?";

        var btn1 = document.createElement("button");
        btn1.setAttribute("class", "btn btn-success card_btn");
        btn1.innerHTML = "To solitaire";
        
        var btn2 = document.createElement("button");
        btn2.setAttribute("class", "btn btn-danger card_btn");
        btn2.innerHTML = "To junk";
    } else {
        var span = document.createElement("span");
        span.setAttribute("class", color_by_number[card.color] + "_card");
        span.innerHTML = card.value;
        
        var btn1 = document.createElement("button");
        btn1.setAttribute("class", "btn btn-success card_btn");
        btn1.innerHTML = "Color hint";
        
        var btn2 = document.createElement("button");
        btn2.setAttribute("class", "btn btn-danger card_btn");
        btn2.innerHTML = "Value hint";
    }

    new_card.appendChild(span);
    new_card.appendChild(btn1);
    new_card.appendChild(btn2);
}

function to_solitaire(card_num) {
    sendMessage(
        "/move",
         "game_name=" + game_name + "&user_id=" + user_id + "&type=solitaire" + "&user_position=" + game_state.my_position + "&card_num=" + card_num
    )
}

function to_junk(card_num) {
    sendMessage(
        "/move",
         "game_name=" + game_name + "&user_id=" + user_id + "&type=junk" + "&user_position=" + game_state.my_position + "&card_num=" + card_num
    )
}

function hint() {
    sendMessage(
        "/move",
         "game_name=" + game_name + "&user_id=" + user_id + "&type=hint" + "&user_position=" + game_state.my_position + "&color=" + + "&value="
    )
}
