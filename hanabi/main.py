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
import urllib
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


class MainPage(webapp2.RequestHandler):
    def get(self):
        user_id = str(random.randint(1, 100000))
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        games_query = Game.query().order(-Game.date)
        games = games_query

        token = channel.create_channel(user_id)
        template_values = {"token": token, "t": user.user_id(), "games": games, "user_id": user_id}
        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(template_values))


class Card(ndb.Model):
    color = ndb.IntegerProperty(indexed=False)
    value = ndb.IntegerProperty(indexed=False)


class Hand(ndb.Model):
    cards = ndb.LocalStructuredProperty(Card, indexed=False, repeated=True)


class GameState(ndb.Model):
    deck = ndb.StructuredProperty(Card, indexed=False, repeated=True)
    solitaire = ndb.StructuredProperty(Card, indexed=False, repeated=True)
    junk = ndb.StructuredProperty(Card, indexed=False, repeated=True)
    user_hands = ndb.LocalStructuredProperty(Hand, indexed=False, repeated=True)

    life_count = ndb.IntegerProperty()
    hint_count = ndb.IntegerProperty()

    whose_move = ndb.IntegerProperty()


class Game(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_id_list = ndb.StringProperty(indexed=False, repeated=True)

    max_user_count = ndb.IntegerProperty(indexed=False)

    game_state = ndb.StructuredProperty(GameState, indexed=False)


class GameCreateHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameCreateHandler post")
        
        game_name = self.request.get("game_name")
        password = self.request.get("password")
        user_id = self.request.get("user_id")
        max_user_count = self.request.get("max_user_count")

        games = Game.query(ancestor=game_key(game_name)).fetch()
        if (len(games) != 0):
            logging.info("Game with name " + game_name + " already exists")
            channel.send_message(user_id, "error?msg=Game with name " + game_name + " already exists")
            return

        game = Game(parent=game_key(game_name))

        game.name = game_name
        game.password = password
        game.user_id_list.append(user_id)
        game.max_user_count = int(max_user_count)
        game.put()

        channel.send_message(user_id, "created")


class JoinGame(webapp2.RequestHandler):
    def post(self):
        logging.info("JoinGame post")

        user_id = self.request.get("user_id")        
        game_name = self.request.get("game_name")
        entered_password = self.request.get("game_password")

        games = Game.query(ancestor=game_key(game_name)).fetch(1)
        if (len(games) != 1):
            logging.info("Wrong game name " + game_name)
            channel.send_message(user_id, "error?msg=Wrong game name")
            return

        game = games[0]

        if (entered_password != game.password):
            logging.info("Wrong password for " + game_name + ", entered: " + entered_password + ", real: " + game.password)
            channel.send_message(user_id, "error?msg=Wrong password")
            return

        if (game.max_user_count <= len(game.user_id_list)):
            logging.info(game_name + " already full")
            channel.send_message(user_id, "error?msg=game already full")
            return

        game.user_id_list.append(user_id)
        game.put()
        logging.info(user_id + " successfully joined into game named " + game_name)
        logging.info("Now in game are: " + ', '.join(game.user_id_list))
        channel.send_message(user_id, "joined?game_name=" + game_name)


class SendChatMessage(webapp2.RequestHandler):
    def post(self):
        logging.info("SendChatMessage post")

        game_name = self.request.get("game_name")
        message = self.request.get("message")

        game = Game.query(ancestor=game_key(game_name)).fetch(1)[0]

        for user_id in game.user_id_list:
            channel.send_message(user_id, "new_message?message=" + message)


class GameHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameHandler post")

        game_name = self.request.get("game_name")

        game = Game.query(ancestor=game_key(game_name)).fetch(1)[0]

        game.game_state.deck = []
        for color in range(1, 6):
            for value in range(1, 6):
                for count in range(0, card_amount_in_deck_by_value[value]):
                    game.game_state.deck.append(Card(color=color, value=value))

        random.shuffle(game.game_state.deck)

        game.game_state.solitaire = []
        game.game_state.junk = []
        game.game_state.life_count = 3
        game.game_state.hint_count = 8

        game.game_state.user_hands = []
        for hand_num in range(len(game.user_id_list)):
            hand = []
            for card_num in range(card_amount_in_hand_by_user_count[len(game.user_id_list)]):
                hand.append(game.game_state.deck.pop())
            game.game_state.user_hands = hand

        game.game_state.whose_move = random.randint(0, len(game.user_id_list) - 1)

        for user_id in game.user_id_list:
            channel.send_message(user_id, "start_game&")


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame),
    ("/game", GameHandler),
    ("/send_chat_message", SendChatMessage)
], debug=True)
