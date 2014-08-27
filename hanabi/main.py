#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import logging
import random

from google.appengine.api import channel
from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors

import jinja2
import webapp2

card_amount_in_deck_by_value = [0, 3, 2, 2, 2, 1]
card_amount_in_hand_by_user_count = [0, 0, 5, 5, 4, 4]
color_by_number = ["undefined", "red", "green", "blue", "yellow", "white"];

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)


def game_key(game_name):
    return ndb.Key("Game", game_name)


def game_state_msg_for_user(game, num):
    msg = "start_game?"
    msg += "life=" + str(game.game_state.life_count)
    msg += "&hint=" + str(game.game_state.hint_count)
    msg += "&whose_move=" + str(game.game_state.whose_move)
    msg += "&your_position=" + str(num)
    msg += "&users_count=" + str(game.user_count)
    msg += "&deck_size=" + str(len(game.game_state.deck))

    for user_num in range(game.user_count):
        msg += "&user" + str(user_num) + "nick=" + game.user_nick_list[user_num]
        if (num != user_num):
            msg += "&user" + str(user_num) + "cards="
            for card in game.game_state.user_hands[user_num].cards:
                msg += str(card.color) + str(card.value)

    msg += "&solitaire="
    for card in game.game_state.solitaire:
        msg += str(card.color) + str(card.value)

    msg += "&junk="
    for card in game.game_state.junk:
        msg += str(card.color) + str(card.value)

    return msg


class Card(ndb.Model):
    color = ndb.IntegerProperty()
    value = ndb.IntegerProperty()


class Hand(ndb.Model):
    cards = ndb.LocalStructuredProperty(Card, repeated=True)


class GameState(ndb.Model):
    deck = ndb.StructuredProperty(Card, repeated=True)
    solitaire = ndb.StructuredProperty(Card, repeated=True)
    junk = ndb.StructuredProperty(Card, repeated=True)
    user_hands = ndb.LocalStructuredProperty(Hand, repeated=True)
    moves_after_empty_deck = ndb.IntegerProperty(default=0)

    life_count = ndb.IntegerProperty()
    hint_count = ndb.IntegerProperty()

    whose_move = ndb.IntegerProperty()


class Game(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_id_list = ndb.StringProperty(repeated=True)
    user_nick_list = ndb.StringProperty(repeated=True)
    started = ndb.BooleanProperty(indexed=True, default=False)
    full = ndb.BooleanProperty(indexed=True)
    user_count = ndb.IntegerProperty(indexed=True, default=0)
    locked = ndb.BooleanProperty(indexed=True, default=False)

    max_user_count = ndb.IntegerProperty()

    game_state = ndb.StructuredProperty(GameState)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user_id = str(random.randint(0, (1 << 31) - 1))

        games_query = Game.query(
            Game.started == False, Game.full == False).order(-Game.date)
        games = games_query

        try:
            token = channel.create_channel(user_id, duration_minutes=24*60)
        except apiproxy_errors.OverQuotaError:
            logging.info("OverQuotaError")
            token = None

        template_values = {
            "token": token,
            "t": user_id,
            "games": games,
            "user_id": user_id
        }

        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(template_values))


class GameCreateHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameCreateHandler post")

        game_name = self.request.get("game_name")
        password = self.request.get("password")
        user_id = self.request.get("user_id")
        nick = self.request.get("nick")
        max_user_count = self.request.get("max_user_count")

        games = Game.query(Game.name == game_name).fetch()
        if len(games) != 0:
            logging.info("Game with name " + game_name + " already exists")
            channel.send_message(
                user_id,
                "alert?type=error&msg=Game with name " + game_name + " already exists"
            )
            return

        game = Game()

        game.name = game_name
        game.password = password
        game.user_id_list.append(user_id)
        game.user_nick_list.append(nick)
        game.user_count = 1
        game.max_user_count = int(max_user_count)
        game.started = False
        game.full = False
        game.locked = (len(game.password) != 0)
        game.put()

        channel.send_message(
            user_id,
            "created?&users_count=" + str(game.user_count) +
            "&users_list=" + nick
        )


@ndb.transactional(retries=4)
def add_user_to_game(game_url, game_name, user_id, nick, entered_password):
    game = ndb.Key(urlsafe=game_url).get()

    if entered_password != game.password:
        logging.info(
            "Wrong password for " + game_name + ", entered: " +
            entered_password + ", real: " + game.password
        )
        channel.send_message(user_id, "alert?type=error&msg=Wrong password")
        return False

    if game.max_user_count <= game.user_count:
        logging.info(game_name + " already full")
        channel.send_message(user_id, "alert?type=error&msg=game already full")
        return False

    if user_id in game.user_id_list:
        logging.info(user_id + " already in " + game_name)
        channel.send_message(
            user_id,
            "alert?type=error&msg=you are already in this game"
        )
        return False

    game.user_id_list.append(user_id)
    game.user_nick_list.append(nick)
    game.user_count += 1
    if (game.user_count >= game.max_user_count):
        game.full = True

    game.put()
    return True


class JoinGame(webapp2.RequestHandler):
    def post(self):
        logging.info("JoinGame post")

        user_id = self.request.get("user_id")
        game_name = self.request.get("game_name")
        entered_password = self.request.get("game_password")
        nick = self.request.get("nick")

        games = Game.query(Game.name == game_name).fetch(1)
        if len(games) != 1:
            logging.info("Wrong game name " + game_name)
            channel.send_message(user_id, "alert?type=error&msg=Wrong game name")
            return

        game_url = games[0].key.urlsafe()
        if not add_user_to_game(game_url, game_name, user_id, nick, entered_password):
            return
        else:
            game = Game.query(Game.name == game_name).fetch(1)[0]

            logging.info(
                user_id + " successfully joined into game named " + game_name
            )
            logging.info("Now in game are: " + ', '.join(game.user_id_list))

            users_str =\
                "&users_list=" + "<br>".join([user for user in game.user_nick_list])
            channel.send_message(
                user_id,
                "joined?&game_name=" + game_name +
                "&started=" + str(game.started) +
                "&users_count=" + str(game.user_count) + users_str
            )

            for user in game.user_id_list:
                if user != user_id:
                    channel.send_message(
                        user,
                        "update_online?users_count=" + str(game.user_count) +
                        users_str
                    )


class SendChatMessage(webapp2.RequestHandler):
    def post(self):
        logging.info("SendChatMessage post")

        game_name = self.request.get("game_name")
        from_id = self.request.get("user_id")
        message = self.request.get("message")
        nick = self.request.get("nick")

        game = Game.query(Game.name == game_name).fetch(1)[0]

        if (message.strip() != ""):
            for user_id in game.user_id_list:
                channel.send_message(
                    user_id,
                    "new_message?from_id=" + nick +
                    "&message=" + message
                )


class GameStartHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameStartHandler post")

        game_name = self.request.get("game_name")

        game = Game.query(Game.name == game_name).fetch(1)[0]

        #game.user_count = 4
        if (game.user_count < 2):
            return

        game.game_state = GameState()

        game.game_state.deck = []
        for color in range(1, 6):
            for value in range(1, 6):
                for count in range(0, card_amount_in_deck_by_value[value]):
                    card = Card(color=color, value=value)
                    game.game_state.deck.append(card)

        random.shuffle(game.game_state.deck)

        game.game_state.solitaire = []
        game.game_state.junk = []
        game.game_state.life_count = 3
        game.game_state.hint_count = 8

        game.game_state.user_hands = []
        for hand_num in range(game.user_count):
            hand = Hand()
            for card_num in range(card_amount_in_hand_by_user_count[game.user_count]):
                hand.cards.append(game.game_state.deck.pop())

            game.game_state.user_hands.append(hand)

        game.game_state.whose_move = random.randint(0, game.user_count - 1)

        game.started = True
        game.put()

        num = 0
        for user_id in game.user_id_list:
            channel.send_message(user_id, game_state_msg_for_user(game, num))
            num += 1


class GameListRefreshHandler(webapp2.RequestHandler):
    def post(self):

        games = Game.query(
            Game.started == False,
            Game.full == False
        ).order(-Game.date).fetch()

        user_id = self.request.get("user_id")
        start = "add_game_to_list?"
        param_string = ""

        num = 0
        for game in games:
            param_string += "&game_name" + str(num) + "=" + game.name +\
            "&users_count" + str(num) + "=" + str(game.user_count) +\
            "&max_users_count" + str(num) + "=" + str(game.max_user_count) +\
            "&locked" + str(num) + "=" + str(game.locked)

            num += 1

        param_string = start + "num=" + str(num) + param_string

        channel.send_message(user_id, param_string)
        logging.info("send " + param_string)


@ndb.transactional(retries=4)
def game_move(request, game_url, user_id):
    game_key = ndb.Key(urlsafe=game_url)
    game = game_key.get()

    move_type = request.get("type")
    user_position = int(request.get("user_position"))
    if (move_type == "junk"):
        card_num = int(request.get("card_num"))
        game.game_state.hint_count = min(8, game.game_state.hint_count + 1)
        card_to_junk = game.game_state.user_hands[user_position].cards.pop(card_num)
        game.game_state.junk.append(card_to_junk)

        first_part = game.game_state.user_hands[user_position].cards[:card_num]
        third_part = game.game_state.user_hands[user_position].cards[card_num:]

        try:
            new_card = game.game_state.deck.pop()
        except:
            game.game_state.moves_after_empty_deck += 1
            new_card = Card(color=0, value=0)

        game.game_state.user_hands[user_position].cards = first_part + [new_card] + third_part

        game.game_state.whose_move += 1
        game.game_state.whose_move %= game.user_count

        num = 0
        for user_id in game.user_id_list:
            channel.send_message(user_id, game_state_msg_for_user(game, num))
            num += 1

    if (move_type == "solitaire"):
        card_num = int(request.get("card_num"))
        cur_card = game.game_state.user_hands[user_position].cards[card_num]

        mx = 0
        for card in game.game_state.solitaire:
            if (card.color == cur_card.color):
                mx = max(mx, card.value)

        if (mx != cur_card.value - 1):
            channel.send_message(user_id, "alert?type=info&msg=Can't put this card to solitaire")
            for user in game.user_id_list:
                if (user != user_id):
                    channel.send_message(user, "alert?type=info&msg=User " + user_id + " tried to put card to solitaire and failed")

            game.game_state.junk.append(cur_card)
            game.game_state.life_count -= 1
            if (game.game_state.life_count == 0):
                num = 0
                for user in game.user_id_list:
                    channel.send_message(user, game_state_msg_for_user(game, num))
                    channel.send_message(user, "alert?type=over&msg=Game Over!")
                    num += 1
                game.key.delete()
                return
        else:
            if (cur_card.value == 1):
                game.game_state.solitaire.append(cur_card)
            else:
                x = 0
                for some_card in game.game_state.solitaire:
                    if (some_card.color == cur_card.color):
                        break
                    x += 1
                game.game_state.solitaire[x] = cur_card
                if (cur_card.value == 5):
                    game.game_state.hint_count = min(8, game.game_state.hint_count + 1)

        game.game_state.user_hands[user_position].cards.pop(card_num)
        first_part = game.game_state.user_hands[user_position].cards[:card_num]
        third_part = game.game_state.user_hands[user_position].cards[card_num:]

        try:
            new_card = game.game_state.deck.pop()
        except:
            game.game_state.moves_after_empty_deck += 1
            new_card = Card(color=0, value=0)

        game.game_state.user_hands[user_position].cards = first_part + [new_card] + third_part

        game.game_state.whose_move += 1
        game.game_state.whose_move %= game.user_count

        num = 0
        for user in game.user_id_list:
            channel.send_message(user, game_state_msg_for_user(game, num))
            num += 1

        x = 0
        for some_card in game.game_state.solitaire:
            if (some_card.value == 5):
                x += 1

        if (x == 5):
            for user in game.user_id_list:
                channel.send_message(user, "alert?type=over&msg=Game Over!")
            game.key.delete()
            return

    if (move_type == "hint"):
        logging.info("hint")
        color = int(request.get("color"))
        value = int(request.get("value"))

        if (game.game_state.hint_count == 0):
            channel.send_message(user_id, "alert?type=error&msg=U have no hints anymore")
            return

        game.game_state.hint_count -= 1

        card_ids = []

        num = 0
        for card in game.game_state.user_hands[user_position].cards:
            if (card.color == color):
                card_ids.append(num)
            elif (card.value == value):
                card_ids.append(num)
            num += 1

        if (len(game.game_state.deck) == 0):
            game.game_state.moves_after_empty_deck += 1

        game.game_state.whose_move += 1
        game.game_state.whose_move %= game.user_count

        num = 0
        for user in game.user_id_list:
            if (color != -1):
                channel.send_message(
                    user,
                    game_state_msg_for_user(game, num) +\
                    "&last_move=hint&from_player=" + str(game.game_state.whose_move) +\
                    "&to_player=" + str(user_position) +\
                    "&type=color" +\
                    "&card_ids=" + "".join(map(str, card_ids)) +\
                    "&hinted_color=" + color_by_number[color]
                )
            else:
                channel.send_message(
                    user,
                    game_state_msg_for_user(game, num) +\
                    "&last_move=hint&from_player=" + str(game.game_state.whose_move) +\
                    "&to_player=" + str(user_position) +\
                    "&type=value" +\
                    "&card_ids=" + "".join(map(str, card_ids)) +\
                    "&hinted_value=" + str(value)
                )
            num += 1

    if (game.user_count == game.game_state.moves_after_empty_deck):
        num = 0
        for user in game.user_id_list:
            channel.send_message(user, game_state_msg_for_user(game, num))
            channel.send_message(user, "alert?type=over&msg=Game Over!")
            num += 1
        game.key.delete()
        return

    game.put()


class GameMoveHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameMoveHandler post")
        user_id = self.request.get("user_id")
        game_name = self.request.get("game_name")

        games = Game.query(Game.name == game_name).fetch(1)

        if (len(games) != 0):
            game = games[0]
        else:
            channel.send_message(user_id, "alert?type=error&msg=Game already over, man...")
            return

        if (game.user_id_list.index(user_id) != game.game_state.whose_move):
            channel.send_message(user_id, "alert?type=error&msg=Not your turn!")
            return

        game_url = game.key.urlsafe()

        game_move(self.request, game_url, user_id)


@ndb.transactional(retries=4)
def user_disconnect(user_id, game_url):
    logging.info("user_disconnect transaction")

    game_key = ndb.Key(urlsafe=game_url)
    game = game_key.get()

    if (game.started):
        for user in game.user_id_list:
            if (user != user_id):
                channel.send_message(user, "alert?type=error&msg=KABOOM user #" + user_id + " gone!!!")
        game.key.delete()
        return False

    j = 0
    while (j < len(game.user_id_list)):
        if (game.user_id_list[j] == user_id):
            game.user_id_list = game.user_id_list[:j] + game.user_id_list[j + 1:]
            game.user_nick_list = game.user_nick_list[:j] + game.user_nick_list[j + 1:]
            break
        else:
            j += 1

    game.user_count = len(game.user_id_list)
    game.full = (game.user_count == game.max_user_count)
    if (game.user_count == 0):
        logging.info("game '" + game.name + "' deleted")
        game.key.delete()
        return False
    else:
        game.put()
        return True


@ndb.transactional(retries=4)
def update_online_users(game_url):
    logging.info("update_online_users transaction")

    game_key = ndb.Key(urlsafe=game_url)
    game = game_key.get()

    users_str = "&users_list=" + "<br>".join([user for user in game.user_nick_list])
    for user in game.user_id_list:
        channel.send_message(user, "update_online?users_count=" + str(game.user_count) + users_str)


class DisconnectionHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("DisconnectionHandler post")

        user_id = self.request.get("from")

        games = Game.query(Game.user_id_list == user_id).fetch(1)

        if (len(games) != 0):
            game_url = games[0].key.urlsafe()
            if (user_disconnect(user_id, game_url)):
                update_online_users(game_url)
        else:
            logging.info("DisconnectionHandler post: game already deleted")


class LeaveHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("LeaveHandler post")

        user_id = self.request.get("user_id")

        games = Game.query(Game.user_id_list == user_id).fetch(1)

        if (len(games) != 0):
            game_url = games[0].key.urlsafe()
            if (user_disconnect(user_id, game_url)):
                update_online_users(game_url)
        else:
            logging.info("LeaveHandler post: game already deleted")


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame),
    ("/start_game", GameStartHandler),
    ("/send_chat_message", SendChatMessage),
    ("/game_list_refresh", GameListRefreshHandler),
    ("/move", GameMoveHandler),
    ("/leave", LeaveHandler),
    ("/_ah/channel/disconnected/", DisconnectionHandler)
], debug = True)
