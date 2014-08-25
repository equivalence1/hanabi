card_amount_in_deck_by_value = [0, 3, 2, 2, 2, 1];
card_amount_in_hand_by_user_count = [0, 0, 5, 5, 4, 4];

color_by_number = ["undefined", "red", "green", "blue", "yellow", "white"];

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
}

function update_game_table() {
    var i = 0;

    place = [];
    place[game_state.my_position] = "down_hand";
    if (game_state.users_count == 2) {
        place[((game_state.my_position + 1) % 2)] = "upper_hand";
    } else {
        for (i = 1; i < game_state.users_count; i++) {
            place[(game_state.my_position + i) % game_state.users_count] = ["left_hand", "upper_hand", "right_hand"][i - 1];
        }
    }

    for (i = 0; i < 4; i++) {
        var div = document.getElementById(["left_hand", "upper_hand", "right_hand", "down_hand"][i]);
        if (div != undefined)
            div.style.backgroundColor = "rgb(247, 247, 249)";
    }

    var div = document.getElementById(place[game_state.whose_move]);
    div.style.backgroundColor = "rgb(223, 240, 216)";

    for (i = 0; i < game_state.users_count; i++) {
        var hand = document.getElementById(place[i]);
        hand.innerHTML = "";
        for (var j = 0; j < card_amount_in_hand_by_user_count[game_state.users_count]; j++)
            add_card_to_hand(hand, game_state.hand[i][j], i, j);
    }

    var table_solitaire = document.getElementById("solitaire");
    table_solitaire.innerHTML = "";
    var time_junk = document.getElementById("time_tab");
    time_junk.innerHTML = "";
    var color_junk = document.getElementById("color_tab");
    color_junk.innerHTML = "";
    var table_chips = document.getElementById("chips");
    table_chips.innerHTML = "";

    var move_info = document.createElement("div");
    move_info.setAttribute("class", "info_message");
    move_info.style.left = "0px";
    move_info.style.width = "150px";

    if (game_state.whose_move == game_state.my_position) {
        move_info.innerHTML = " It's your move!";
    } else {
        move_info.innerHTML = " It's not your move!";
    }
    move_info.style.top = "280px";
    table_chips.appendChild(move_info);

    var scores = document.createElement("div");
    scores.setAttribute("class", "info_message");
    scores.style.left = "75px";
    scores.innerHTML = "Score: " + game_state.score;
    table_chips.appendChild(scores);

    var deck_size = document.createElement("div");
    deck_size.setAttribute("class", "info_message");
    deck_size.style.left = "0px";
    deck_size.innerHTML = "Deck: " + game_state.deck_size;
    table_chips.appendChild(deck_size);

    add_chips(table_chips);

    add_cards_to_solitaire(table_solitaire, game_state.solitaire);

    add_cards_to_junk(time_tab, game_state.junk);
    add_cards_to_junk(color_tab, game_state.junk);

    if (hint != undefined) {
        display_hint();
        hint = undefined;
    }

    var players_order_div = document.getElementById("players_order");
    players_order_div.innerHTML = "";
    var nick_list = document.createElement("p");
    for (i = 0; i < game_state.users_count; i++) {
        if (i != game_state.users_count - 1)
            var s = game_state.user_nick_list[(game_state.my_position + i) % game_state.users_count] + " → ";
        else
            var s = game_state.user_nick_list[(game_state.my_position + i) % game_state.users_count];
        var sp = document.createElement("span");
        sp.innerHTML = s;
        if ((game_state.my_position + i) % game_state.users_count == game_state.whose_move)
            sp.setAttribute("class", "green_card");
        nick_list.appendChild(sp);
    }
    players_order_div.appendChild(nick_list);

}

function add_chips(table_chips) {
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
}

function add_card_to_hand(hand, card, whose_hand, card_id_in_hand) {
    var new_card = document.createElement("div");
    new_card.setAttribute("class", "card");
    new_card.setAttribute("whose_hand", whose_hand);
    new_card.setAttribute("card_id_in_hand", card_id_in_hand);
    
    var card_content = document.createElement("div");
    card_content.setAttribute("class", "card_content");
    card_content.setAttribute("whose_hand", whose_hand);
    card_content.setAttribute("card_id_in_hand", card_id_in_hand);

    var card_over = document.createElement("div");
    card_over.setAttribute("class", "card_over");
    card_over.setAttribute("whose_hand", whose_hand);
    card_over.setAttribute("card_id_in_hand", card_id_in_hand);
    card_over.setAttribute("id", whose_hand * 10 + card_id_in_hand);

    if (card != undefined && card.value != 0) {
        card_over.setAttribute("card_color", card.color);
        card_over.setAttribute("card_value", card.value);
    }
    
    var span = document.createElement("span");
    var btn1 = document.createElement("button");
    var btn2 = document.createElement("button");

    card_content.appendChild(span);
    if ((card != undefined && card.value != 0) || (card == undefined)) {
        card_over.appendChild(btn1);
        card_over.appendChild(btn2);
    }

    if (card == undefined || card.value == 0) {
        span.setAttribute("class", "undefined_card");
        span.setAttribute("value", "?");
        if (card == undefined)
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

function add_cards_to_solitaire(sol, cards) {
    var highest_card = [-1, 0, 0, 0, 0, 0];
    for (var i = 0; i < cards.length; i++)
        highest_card[cards[i].color] = Math.max(highest_card[cards[i].color], cards[i].value);

    for (var color = 1; color <= 5; color++) {
        for (var value = 1; value <= highest_card[color]; value++) {
            var new_card = document.createElement("div");
            new_card.setAttribute("class", "card_solitaire");
            new_card.style.left = (color - 1) * (64 + 20) + 15 + "px";
            new_card.style.top = 10 * (value - 1) + 3 + "px";

            var card_content = document.createElement("div");
            card_content.setAttribute("class", "card_content");

            var span = document.createElement("span");
            card_content.appendChild(span);

            span.setAttribute("class", color_by_number[color] + "_card");
            span.innerHTML = value;

            new_card.appendChild(card_content);

            sol.appendChild(new_card);
        }
    }
}

function add_cards_to_junk(junk, cards) {
    if (junk.id === "time_tab")
        for (var i = 0; i < cards.length; i++) {
            var new_mini_card = document.createElement("div");
            new_mini_card.setAttribute("class", "mini_card");

            var card_content = document.createElement("div");
            card_content.setAttribute("class", "mini_card_content");

            var span = document.createElement("span");
            span.setAttribute("class", color_by_number[cards[i].color] + "_card");
            span.innerHTML = cards[i].value;

            card_content.appendChild(span);
            new_mini_card.appendChild(card_content);
            junk.appendChild(new_mini_card);
        }
    else {
        var color_tab_cards = [[], [], [], [], []];
        for (var i = 0; i < cards.length; i++) {
            color_tab_cards[cards[i].color - 1].push(cards[i].value);
        }
        for (var i = 0; i < 5; i++) {
            color_tab_cards[i].sort();
            for (var j = 0; j < color_tab_cards[i].length; j++) {
                var new_mini_card = document.createElement("div");
                new_mini_card.setAttribute("class", "mini_card");

                var card_content = document.createElement("div");
                card_content.setAttribute("class", "mini_card_content");

                var span = document.createElement("span");
                span.setAttribute("class", color_by_number[i + 1] + "_card");
                span.innerHTML = color_tab_cards[i][j];

                card_content.appendChild(span);
                new_mini_card.appendChild(card_content);
                junk.appendChild(new_mini_card);
            }

            var br = document.createElement("br");
            junk.appendChild(br);
        }
    }
}

function start_animation(arrow) {
    function frame() {
        if (arrow == undefined)
            clearInterval(timer);

        arrow.time += step;
        if (arrow.left_animated)
            arrow.style.left = (arrow.start_left + (Math.sin(arrow.time) * 10)) + "px";
        if (arrow.top_animated)
            arrow.style.top = (arrow.start_top + (Math.sin(arrow.time) * 10)) + "px";
    }

    var timer = setInterval(frame, 10);
}

function display_hint() {
    for (var i = 0; i < hint.card_ids.length; i++) {
        var arrow = document.createElement("div");
        arrow.setAttribute("class", "arrow");
        arrow.time = 0;

        if (hint.hinted_color != undefined)
            arrow.style.color = hint.hinted_color;
        else
            arrow.style.color = "lightgray";

        if (place[hint.to_player] == "down_hand") {
            if (hint.hinted_color != undefined)
                arrow.innerHTML = hint.hinted_color;
            else
                arrow.innerHTML = hint.hinted_value;
            arrow.innerHTML += "<br>";

            arrow.innerHTML += "↓";
            arrow.start_top = -70;
            arrow.start_left = 32 + parseInt(hint.card_ids[i]) * 67;
            arrow.style.top = "-70px";
            arrow.style.left = (32 + parseInt(hint.card_ids[i]) * 67) + "px";
            arrow.left_animated = false;
            arrow.top_animated = true;
        }

        if (place[hint.to_player] == "upper_hand") {
            arrow.innerHTML = "↑";
            arrow.start_top = 80;
            arrow.start_left = 32 + parseInt(hint.card_ids[i]) * 67;
            arrow.style.top = "80px";
            arrow.style.left = (32 + parseInt(hint.card_ids[i]) * 67) + "px";
            arrow.left_animated = false;
            arrow.top_animated = true;

            arrow.innerHTML += "<br>";
                if (hint.hinted_color != undefined)
            arrow.innerHTML += hint.hinted_color;
            else
                arrow.innerHTML += hint.hinted_value;
        }

        if (place[hint.to_player] == "left_hand") {
            arrow.innerHTML = "←";
            if (hint.hinted_color != undefined)
                arrow.innerHTML += hint.hinted_color;
            else
                arrow.innerHTML += hint.hinted_value;

            arrow.start_left = 70;
            arrow.start_top = 50 + parseInt(hint.card_ids[i]) * 99;
            arrow.style.left = "70px";
            arrow.style.top = (50 + parseInt(hint.card_ids[i]) * 99) + "px";
            arrow.left_animated = true;
            arrow.top_animated = false;
        }

        if (place[hint.to_player] == "right_hand") {
            if (hint.hinted_color != undefined)
                arrow.innerHTML = hint.hinted_color;
            else
                arrow.innerHTML = hint.hinted_value;
            arrow.innerHTML += "→";
            arrow.start_left = -70;
            arrow.start_top = 50 + parseInt(hint.card_ids[i]) * 99;
            arrow.style.left = arrow.start_left + "px";
            arrow.style.top = (50 + parseInt(hint.card_ids[i]) * 99) + "px";
            arrow.left_animated = true;
            arrow.top_animated = false;
        }



        var hand = document.getElementById(place[hint.to_player]);
        hand.appendChild(arrow);
        start_animation(arrow);
    }
}

function to_solitaire() {
    sendMessage(
        "/move",
         "game_name=" + game_name +
         "&user_id=" + user_id +
         "&type=solitaire" +
         "&user_position=" + game_state.my_position +
         "&card_num=" + this.parentNode.getAttribute("card_id_in_hand")
    )
}

function to_junk() {
    sendMessage(
        "/move",
        "game_name=" + game_name +
        "&user_id=" + user_id +
        "&type=junk" +
        "&user_position=" + game_state.my_position +
        "&card_num=" + this.parentNode.getAttribute("card_id_in_hand")
    )
}

function color_hint() {
    var whose_hand = this.parentNode.getAttribute("whose_hand");
    var color = this.parentNode.getAttribute("card_color");
    var val = -1;

    sendMessage(
        "/move",
        "game_name=" + game_name +
        "&user_id=" + user_id +
        "&type=hint" +
        "&user_position=" + whose_hand +
        "&color=" + color +
        "&value=" + val
    )
}

function value_hint() {
    var whose_hand = this.parentNode.getAttribute("whose_hand");
    var color = -1;
    var val = this.parentNode.getAttribute("card_value");

    sendMessage(
        "/move",
        "game_name=" + game_name +
        "&user_id=" + user_id +
        "&type=hint" +
        "&user_position=" + whose_hand +
        "&color=" + color +
        "&value=" + val
    )
}
