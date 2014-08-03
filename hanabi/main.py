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
        if num != user_num:
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

        token = channel.create_channel(user_id)
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

        users_str = "&users_list=" + user_id
        channel.send_message(
            user_id,
            "created?&users_count=" + str(game.user_count) + users_str
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
            user_id, "joined?game_name=" + game_name + "&started=" +
            str(game.started) + "&users_count=" + str(game.user_count) +
            users_str
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
                user_id, "new_message?from_id=" + from_id + "&message=" +
                message
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


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame),
    ("/start_game", GameStartHandler),
    ("/send_chat_message", SendChatMessage),
    ("/game_list_refresh", GameListRefreshHandler),
], debug = True)
