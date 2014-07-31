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
    table.innerHTML = "";

    for (i = 0; i < 3 - game_state.life; i++) {
        var dead_life = document.createElement("div");
        dead_life.setAttribute("class", "dead_life_chip");
        dead_life.setAttribute("left", (450 - (3 - i) * 10).toString() + "px");
        table.appendChild(dead_life);
    }

    for (; i < 3; i++) {
        var alive_life = document.createElement("div");
        alive_life.setAttribute("class", "alive_life_chip");
        alive_life.setAttribute("style", "left:" + ((450 - (3 - i) * 10).toString() + "px"));
        table.appendChild(alive_life);
    }


}

function add_card_to_hand(hand, card) {
    if (card == undefined)
        hand.innerHTML += "<div class='card'><span class='undefined_card'>?</span></div>";
    else
        hand.innerHTML += "<div class='card'><span class='" + color_by_number[card.color] + "_card'>" + card.value + "</span></div>";

    hand.innerHTML += "</div>";
}
