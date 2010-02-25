"""
    appengine for gae version of mycloud server

    Copyright (C) 2010  Pan, Shi Zhu

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import algo
import urllib
import string

def myrot13(input):
    a = "12345abcdefghijklmABCDEFGHIJKLM"
    b = "98760nopqrstuvwxyzNOPQRSTUVWXYZ"
    return input.translate(string.maketrans(a+b, b+a))

def mydecode(key, hint, ptr):
    src = urllib.quote(key)
    dest = '%s\t%d\t%s\n' % (src, ptr, hint.replace(" ", "_"))
    return myrot13(dest)

def myencode(key):
    return myrot13(key)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        file = open("index.html", "r")
        self.response.out.write(file.read())
        file.close()

class QuanPin(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=quanpin")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

class ShuangPinAbc(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=abc")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

class ShuangPinMs(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=ms")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

class Wubi(webapp.RequestHandler):
    def get(self, keyb):
        self.response.headers['Content-Type'] = 'text/plain'
        algo.parse("__setmode=wubi")
        algo.parse("__setgae=1")
        for k, h, v in algo.parse(myencode(keyb)):
            self.response.out.write(mydecode(k,h,v))

application = webapp.WSGIApplication([
                                     ('/', MainPage),
                                     ('/qp/(.*)', QuanPin),
                                     ('/abc/(.*)', ShuangPinAbc),
                                     ('/ms/(.*)', ShuangPinMs),
                                     ('/wb/(.*)', Wubi),
                                         ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
