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
        user_id = str(random.randint(1, 100000));
        user = users.get_current_user()
        
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        games_query = Game.query()
        games = games_query

        token = channel.create_channel(user_id)
        template_values = {"token": token, "t": user.user_id(), "games": games}
        template = JINJA_ENVIRONMENT.get_template("index.html")
        self.response.write(template.render(template_values))


class TestHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("TestHandler post")
        channel.send_message(user_id, self.request.get("data"))


class Game(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)


class GameCreateHandler(webapp2.RequestHandler):
    def post(self):
        logging.info("GameCreateHandler post")
        
        game_name = self.request.get("game_name")
        password = self.request.get("password")

        game = Game(parent=game_key(game_name));

        game.name = game_name
        game.password = password
        game.put()


class JoinGame(webapp2.RequestHandler):
    def post(self):
        logging.info("JoinGame post")
        
        game_name = self.request.get("game_name")
        games = Game.query(ancestor=game_key(game_name))
        for game in games:            
            logging.info("Password from room '" + game_name + "' is: " + game.password);


application = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/test", TestHandler),
    ("/game_create", GameCreateHandler),
    ("/join_game", JoinGame)
], debug=True)
