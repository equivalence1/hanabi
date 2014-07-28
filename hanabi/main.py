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


class Game(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    user_list = ndb.StringProperty(indexed=False, repeated=True)


class GameCreateHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameCreateHandler post")
        
        game_name = self.request.get("game_name")
        password = self.request.get("password")

        games = Game.query(ancestor=game_key(game_name)).fetch()
        if (len(games) != 0):
            return

        game = Game(parent=game_key(game_name))

        game.name = game_name
        game.password = password
        game.put()


class JoinGame(webapp2.RequestHandler):
    def post(self):
        logging.info("JoinGame post")

        user_id = self.request.get("user_id")        
        game_name = self.request.get("game_name")
        entered_password = self.request.get("game_password")

        game = Game.query(ancestor=game_key(game_name)).fetch(1)[0]

        if (entered_password != game.password):
            logging.info("Wrong password for " + game_name + ", entered: " + entered_password + ", real: " + game.password)
            channel.send_message(user_id, "Wrong password")
            return

        game.user_list.append(user_id)
        game.put()
        logging.info(user_id + " successfully joined into game named " + game_name)
        logging.info("Now in game are: " + ', '.join(game.user_list))
        channel.send_message(user_id, "Successfully joined into game named $" + game_name + "$. Already in the game: " + ', '.join(game.user_list))

        template = JINJA_ENVIRONMENT.get_template("game_chat_screen.html")
        self.response.write(template.render())


class SendChatMessage(webapp2.RequestHandler):
    def get(self):
        pass

    def post(self):
        pass


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame),
    ("/send_chat_message", SendChatMessage)
], debug=True)
