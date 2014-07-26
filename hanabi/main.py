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
import webapp2


MAIN_PAGE_HTML = """\
<!DOCTYPE HTML>
<html>
    <head>

        <title> Hanabi </title>
        <link rel="stylesheet" type="text/css" href="stylesheets/start_screen.css">
        <link href="http://s3.amazonaws.com/codecademy-content/courses/ltp/css/shift.css" rel="stylesheet">

    </head>

    <body>

        <div class="nav">
           <div class="container">
               <p id="hanabi_online"> Hanabi online! </p>
           </div>
        </div>

        <div class="room_list">
            <div class="container">
                <p> some message for u </p>
            </div>
        </div>

        <div class="main_menu">
            <div class="container">
                <div class="game_create">
                    <p> some message for u 2 </p>
                </div>
            </div>
        </div>

        <div class="friend_zone">
            <div class="container">
                <p> third message for u </p>
                <a href="test_screen.html"> link here </a>
            </div>
        </div>

    </body>
</html>
"""


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_PAGE_HTML)

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
