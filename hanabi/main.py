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
from google.appengine.api import users
from google.appengine.ext import ndb

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

    for user_num in range(game.user_count):
        if (num != user_num):
            msg += "&user" + str(user_num) + "id=" + game.user_id_list[num]
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

    life_count = ndb.IntegerProperty()
    hint_count = ndb.IntegerProperty()

    whose_move = ndb.IntegerProperty()


class Game(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_id_list = ndb.StringProperty(repeated=True)
    started = ndb.BooleanProperty(indexed=True, default=False)
    full = ndb.BooleanProperty(indexed=True)
    user_count = ndb.IntegerProperty(indexed=True, default=0)
    locked = ndb.BooleanProperty(indexed=True, default=False)

    max_user_count = ndb.IntegerProperty()

    game_state = ndb.StructuredProperty(GameState)


class MainPage(webapp2.RequestHandler):
    def get(self):
        user_id = str(random.randint(0, (1 << 31) - 1))
        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        games_query = Game.query(
            Game.started == False, Game.full == False).order(-Game.date)
        games = games_query

        token = channel.create_channel(user_id, duration_minutes=24*60)
        template_values = {
            "token": token,
            "t": user.user_id(),
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
        max_user_count = self.request.get("max_user_count")

        games = Game.query(Game.name == game_name).fetch()
        if len(games) != 0:
            logging.info("Game with name " + game_name + " already exists")
            channel.send_message(
                user_id,
                "error?msg=Game with name " + game_name + " already exists"
            )
            return

        game = Game()

        game.name = game_name
        game.password = password
        game.user_id_list.append(user_id)
        game.user_count = 1
        game.max_user_count = int(max_user_count)
        game.started = False
        game.full = False
        logging.info(len(game.password) != 0)
        game.locked = (len(game.password) != 0)
        game.put()

        channel.send_message(
            user_id,
            "created?game_url=" + game.key.urlsafe() +
            "&users_count=" + str(game.user_count) +
            "&users_list=" + user_id
        )


class JoinGame(webapp2.RequestHandler):
    def post(self):
        logging.info("JoinGame post")

        user_id = self.request.get("user_id")
        game_name = self.request.get("game_name")
        entered_password = self.request.get("game_password")

        games = Game.query(Game.name == game_name).fetch(1)
        if len(games) != 1:
            logging.info("Wrong game name " + game_name)
            channel.send_message(user_id, "error?msg=Wrong game name")
            return

        game = games[0]

        if entered_password != game.password:
            logging.info(
                "Wrong password for " + game_name + ", entered: " +
                entered_password + ", real: " + game.password
            )
            channel.send_message(user_id, "error?msg=Wrong password")
            return

        if game.max_user_count <= game.user_count:
            logging.info(game_name + " already full")
            channel.send_message(user_id, "error?msg=game already full")
            return

        if user_id in game.user_id_list:
            logging.info(user_id + " already in " + game_name)
            channel.send_message(
                user_id,
                "error?msg=you are already in this game"
            )
            pass

        game.user_id_list.append(user_id)
        game.user_count += 1
        if (game.user_count >= game.max_user_count):
            game.full = True

        game.put()

        logging.info(
            user_id + " successfully joined into game named " + game_name
        )
        logging.info("Now in game are: " + ', '.join(game.user_id_list))

        users_str =\
            "&users_list=" + "<br>".join([user for user in game.user_id_list])
        channel.send_message(
            user_id,
            "joined?game_url=" + game.key.urlsafe() +
            "&game_name=" + game_name +
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

        game = Game.query(Game.name == game_name).fetch(1)[0]

        for user_id in game.user_id_list:
            channel.send_message(
                user_id,
                "new_message?from_id=" + from_id +
                "&message=" + message
            )


class GameStartHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameStartHandler post")

        game_name = self.request.get("game_name")

        game = Game.query(Game.name == game_name).fetch(1)[0]

        game.user_count = 4
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
        games_query = Game.query(
            Game.started == False,
            Game.full == False
        ).order(-Game.date)
        games = games_query

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


class GameMoveHandler(webapp2.RequestHandler):
    def post(self):
        move_type = self.request.get("type")
        user_id = self.request.get("user_id")
        game_name = self.request.get("game_name")
        user_position = int(self.request.get("user_position"))
        game = Game.query(Game.name == game_name).fetch(1)[0]

        if (game.game_state.life_count == 0):
            num = 0
            for user in game.user_id_list:
                channel.send_message(user, "error?msg=Game Over!")
                num += 1
            return

        if (move_type == "junk"):
            card_num = int(self.request.get("card_num"))
            game.game_state.hint_count = min(8, game.game_state.hint_count + 1)
            card_to_junk = game.game_state.user_hands[user_position].cards.pop(card_num)
            game.game_state.junk.append(card_to_junk)

            first_part = game.game_state.user_hands[user_position].cards[:card_num]
            third_part = game.game_state.user_hands[user_position].cards[card_num:]
            new_card = game.game_state.deck.pop()

            game.game_state.user_hands[user_position].cards = first_part + [new_card] + third_part

            num = 0
            for user_id in game.user_id_list:
                channel.send_message(user_id, game_state_msg_for_user(game, num))
                num += 1

        if (move_type == "solitaire"):
            card_num = int(self.request.get("card_num"))
            cur_card = game.game_state.user_hands[user_position].cards[card_num]

            mx = 0
            for card in game.game_state.solitaire:
                if (card.color == cur_card.color):
                    mx = max(mx, card.value)

            if (mx != cur_card.value - 1):
                channel.send_message(user_id, "error?msg=Cant put this card to solitaire")
                for user in game.user_id_list:
                    if (user != user_id):
                        channel.send_message(user, "error?msg=User " + user_id + " tried to put card to solitaire and failed")

                game.game_state.junk.append(cur_card)
                game.game_state.life_count -= 1
                if (game.game_state.life_count == 0):
                    num = 0
                    for user in game.user_id_list:
                        channel.send_message(user, game_state_msg_for_user(game, num))
                        channel.send_message(user, "error?msg=Game Over!")
                        num += 1
                    game.put()
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

            game.game_state.user_hands[user_position].cards.pop(card_num)
            first_part = game.game_state.user_hands[user_position].cards[:card_num]
            third_part = game.game_state.user_hands[user_position].cards[card_num:]
            new_card = game.game_state.deck.pop()

            game.game_state.user_hands[user_position].cards = first_part + [new_card] + third_part

            num = 0
            for user in game.user_id_list:
                channel.send_message(user, game_state_msg_for_user(game, num))
                num += 1


        if (move_type == "hint"):
            logging.info("hint")
            color = int(self.request.get("color"))
            value = int(self.request.get("value"))

            if (game.game_state.hint_count == 0):
                channel.send_message(user_id, "error?msg=U have no hints anymore")
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

            for user in game.user_id_list:
                if (color != -1):
                    channel.send_message(
                        user,
                        "hint?msg=Player " + user_id + " hinted to player " +\
                        game.user_id_list[user_position] + " that cards number " +\
                        ", ".join(map(str, card_ids)) + "are all have color " + color_by_number[color]
                    )
                else:
                    channel.send_message(
                        user,
                        "hint?msg=Player " + user_id + " hinted to player " +\
                        game.user_id_list[user_position] + " that cards number " +\
                        ", ".join(map(str, card_ids)) + "are all have value " + str(value)
                    )

            num = 0
            for user in game.user_id_list:
                channel.send_message(user, game_state_msg_for_user(game, num))
                num += 1

        game.put()


@ndb.transactional(retries=4)
def user_disconnect(user_id, game_url):
    logging.info("user_disconnect transaction")

    game_key = ndb.Key(urlsafe=game_url)
    game = game_key.get()

    if game.started:
        for user in game.user_id_list:
            if user != user_id:
                channel.send_message(user, "error?KABOOM user #" + user_id + " gone!!!")
        return False

    j = 0
    while j < len(game.user_id_list):
        if game.user_id_list[j] == user_id:
            game.user_id_list = game.user_id_list[:j] + game.user_id_list[j + 1:]
        else:
            j += 1

    game.user_count = len(game.user_id_list)
    game.full = (game.user_count == game.max_user_count)
    if game.user_count == 0:
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

    users_str = "&users_list=" + "<br>".join([user for user in game.user_id_list])
    for user in game.user_id_list:
        channel.send_message(user, "update_online?users_count=" + str(game.user_count) + users_str)


class DisconnectionHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("DisconnectionHandler post")

        user_id = self.request.get("from")
        game_url = Game.query(Game.user_id_list == user_id).fetch(1)[0].key.urlsafe()
        if user_disconnect(user_id, game_url):
            update_online_users(game_url)


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame),
    ("/start_game", GameStartHandler),
    ("/send_chat_message", SendChatMessage),
    ("/game_list_refresh", GameListRefreshHandler),
    ("/move", GameMoveHandler),
    ("/_ah/channel/disconnected/", DisconnectionHandler)
], debug = True)
