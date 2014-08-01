card_amount_in_deck_by_value = [0, 3, 2, 2, 2, 1];
card_amount_in_hand_by_user_count = [0, 0, 5, 5, 4, 4];

color_by_number = ["undefined", "red", "green", "blue", "yellow", "white"];

function update_game_table(game_state) {
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
            add_card_to_hand(hand, game_state.hand[i][j]);
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

function add_card_to_hand(hand, card) {
    if (card == undefined)
        hand.innerHTML += "<div class='card'><span class='undefined_card'>?</span></div>";
    else
        hand.innerHTML += "<div class='card'><span class='" + color_by_number[card.color] + "_card'>" + card.value + "</span></div>";
}
