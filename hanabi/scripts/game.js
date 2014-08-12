card_amount_in_deck_by_value = [0, 3, 2, 2, 2, 1];
card_amount_in_hand_by_user_count = [0, 0, 5, 5, 4, 4];

color_by_number = ["undefined", "red", "green", "blue", "yellow", "white"];

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
};

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

//    var table = document.getElementById("table");
//    table.innerHTML = "";

    var table_solitaire = document.getElementById("solitaire");
    table_solitaire.innerHTML = "";
    var table_junk = document.getElementById("junk");
    table_junk.innerHTML = "";
    var table_chips = document.getElementById("chips");
    table_chips.innerHTML = "";

    var scores = document.createElement("div");
    scores.setAttribute("class", "score_message");
    scores.innerHTML = "Scores: " + game_state.solitaire.length.toString();
    table_chips.appendChild(scores);

    for (i = 0; i < 3 - game_state.life; i++) {
        var dead_life = document.createElement("div");
        dead_life.setAttribute("class", "chip");
        dead_life.innerHTML = "<img src='images/dead_life.png'>";
        dead_life.style.left = (50 * i).toString() + "px";
        dead_life.style.top = "30px";
        table_chips.appendChild(dead_life);
    }

    for (; i < 3; i++) {
        var alive_life = document.createElement("div");
        alive_life.setAttribute("class", "chip");
        alive_life.innerHTML = "<img src='images/alive_life.png'>";
        alive_life.style.left = (50 * i).toString() + "px";
        alive_life.style.top = "30px";
        table_chips.appendChild(alive_life);
    }

    for (i = 0; i < 8 - game_state.hint; i++) {
        var dead_hint = document.createElement("div");
        dead_hint.setAttribute("class", "chip");
        dead_hint.innerHTML = "<img src='images/dead_hint.png'>"
        dead_hint.style.left = (50 + 50 * (i % 2)).toString() + "px";
        dead_hint.style.top = (80 + 50 * (i / 2 | 0)).toString() + "px";
        table_chips.appendChild(dead_hint);
    }

    for (; i < 8; i++) {
        var alive_hint = document.createElement("div");
        alive_hint.setAttribute("class", "chip");
        alive_hint.innerHTML = "<img src='images/alive_hint.png'>";
        alive_hint.style.left = (50 + 50 * (i % 2)).toString() + "px";
        alive_hint.style.top = (80 + 50 * (i / 2 | 0)).toString() + "px";
        table_chips.appendChild(alive_hint);
    }

    for (i = 0; i < game_state.solitaire.length; i++) {
        add_card_to_soliter(table_solitaire, game_state.solitaire[i]);
    }

    for (i = 0; i < game_state.junk.length; i++) {

    }
}

function add_card_to_hand(hand, card, whoes_hand, card_id_in_hand) {
    var new_card = document.createElement("div");
    new_card.setAttribute("class", "card");
    new_card.setAttribute("whoes_hand", whoes_hand);
    new_card.setAttribute("card_id_in_hand", card_id_in_hand);
    
    var card_content = document.createElement("div");
    card_content.setAttribute("class", "card_content");
    card_content.setAttribute("whoes_hand", whoes_hand);
    card_content.setAttribute("card_id_in_hand", card_id_in_hand);

    var card_over = document.createElement("div");
    card_over.setAttribute("class", "card_over");
    card_over.setAttribute("whoes_hand", whoes_hand);
    card_over.setAttribute("card_id_in_hand", card_id_in_hand);
    card_over.setAttribute("id", whoes_hand * 10 + card_id_in_hand);

    if (card != undefined) {
        card_over.setAttribute("card_color", card.color);
        card_over.setAttribute("card_value", card.value);
    }
    
    var span = document.createElement("span");
    var btn1 = document.createElement("button");
    var btn2 = document.createElement("button");

    card_content.appendChild(span);
    card_over.appendChild(btn1);
    card_over.appendChild(btn2);

    if (card == undefined) {
        span.setAttribute("class", "undefined_card");
        span.setAttribute("value", "?");
        span.innerHTML = "?";

        btn1.setAttribute("class", "btn btn-success card_btn");
        btn1.innerHTML = "Solitaire";
        btn1.onclick = to_solitaire;
        
        btn2.setAttribute("class", "btn btn-danger card_btn");
        btn2.innerHTML = "Junk";
        btn2.onclick = to_junk;
    } else {
        span.setAttribute("class", color_by_number[card.color] + "_card");
        span.innerHTML = card.value;
        
        btn1.setAttribute("class", "btn btn-success card_btn");
        btn1.innerHTML = color_by_number[card.color];
        btn1.onclick = color_hint;
        
        btn2.setAttribute("class", "btn btn-danger card_btn");
        btn2.innerHTML = card.value;
        btn2.onclick = value_hint;
    }

    new_card.appendChild(card_content);
    new_card.appendChild(card_over);
    hand.appendChild(new_card);
}

function add_card_to_soliter(sol, card) {
    var new_card = document.createElement("div");
    new_card.setAttribute("class", "card " + color_by_number[card.color] + "_card_solitaire card_soliter");

    var card_content = document.createElement("div");
    card_content.setAttribute("class", "card_content");
    
    var span = document.createElement("span");

    card_content.appendChild(span);

    span.setAttribute("class", color_by_number[card.color] + "_card");
    span.innerHTML = card.value;

    var a = document.getElementsByClassName(color_by_number[card.color] + "_card_solitaire");
    var prev_card = a[a.length - 1]

    new_card.style.position = "relative";
    new_card.appendChild(card_content);

    sol.appendChild(new_card);
}

function to_solitaire() {
    sendMessage(
        "/move",
         "game_name=" + game_name + "&user_id=" + user_id + "&type=solitaire" + "&user_position=" + game_state.my_position + "&card_num=" + this.parentNode.getAttribute("card_id_in_hand")
    )
}

function to_junk() {
    sendMessage(
        "/move",
         "game_name=" + game_name + "&user_id=" + user_id + "&type=junk" + "&user_position=" + game_state.my_position + "&card_num=" + this.parentNode.getAttribute("card_id_in_hand")
    )
}

function color_hint() {
    var whoes_hand = this.parentNode.getAttribute("whoes_hand");
    var color = this.parentNode.getAttribute("card_color");
    var val = -1;

    sendMessage(
        "/move",
        "game_name=" + game_name + "&user_id=" + user_id + "&type=hint" + "&user_position=" + whoes_hand + "&color=" + color + "&value=" + val
    )
}

function value_hint() {
    var whoes_hand = this.parentNode.getAttribute("whoes_hand");
    var color = -1;
    var val = this.parentNode.getAttribute("card_value");

    sendMessage(
        "/move",
        "game_name=" + game_name + "&user_id=" + user_id + "&type=hint" + "&user_position=" + whoes_hand + "&color=" + color + "&value=" + val
    )
}
