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

import os
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import algo
import urllib
import string
import mypwd

class im_record(db.Model):
    keyb = db.StringProperty()
    content = db.StringProperty(multiline=True)

def myrot13(input):
    a = "12345abcdefghijklmABCDEFGHIJKLM"
    b = "98760nopqrstuvwxyzNOPQRSTUVWXYZ"
    return input.translate(string.maketrans(a+b, b+a))

def mydecode(key, hint, ptr):
    src = urllib.quote(key)
    dest = '%s\t%d\t%s\n' % (src, ptr, hint.replace(" ", "_"))
    return myrot13(dest)

def myencode(key):
    src = urllib.unquote(key)
    return myrot13(src)

def std_parse(self, keyb, mode):
    self.response.headers['Content-Type'] = 'text/plain'
    algo.parse("__setmode="+mode)
    algo.parse("__setgae=1")
    for k, h, v in algo.parse(myencode(keyb)):
        self.response.out.write(mydecode(k,h,v))

def use_template(self, filename, template_arg):
    self.response.headers['Content-Type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), filename)
    self.response.out.write(template.render(path, template_arg))

class MainPage(webapp.RequestHandler):
    def get(self):
        use_template(self, "index.html", {})

class QuanPin(webapp.RequestHandler):
    def get(self, keyb):
        std_parse(self, keyb, "quanpin")

class ShuangPinAbc(webapp.RequestHandler):
    def get(self, keyb):
        std_parse(self, keyb, "abc")

class ShuangPinMs(webapp.RequestHandler):
    def get(self, keyb):
        std_parse(self, keyb, "ms")

class Wubi(webapp.RequestHandler):
    def get(self, keyb):
        std_parse(self, keyb, "wubi")

class PwdTool(webapp.RequestHandler):
    def get(self, keyb):
        std_parse(self, keyb, "pwd")

class AbcPost(webapp.RequestHandler):
    def get(self):
        use_template(self, "pim.html", { })
    def post(self):
        use_template(self, "pim.html", { })

class PwdPost(webapp.RequestHandler):
    def get(self):
        use_template(self, "pwd.html", {
            'arg1' : '',
            'arg2' : '',
            'result' : '',
            })
    def post(self):
        strkey = self.request.get("arg1")
        strpwd = self.request.get("arg2")
        if len(strpwd) == 0:
            if len(strkey) == 0:
                op = mypwd.public_encrypt(mypwd.KEYSTR, "gae")
            else:
                sp = strkey.partition("@")
                if len(sp[0]) == 0:
                    op = []
                elif len(sp[1]) == 0 or len(sp[2]) == 0:
                    op = mypwd.public_encrypt(mypwd.KEYSTR, sp[0])
                else:
                    op = mypwd.public_encrypt(sp[2], sp[0])
        else:
            op = mypwd.public_encrypt(strpwd, strkey)
        resl = []
        x = 0
        for item in op:
            resl.append("%02d %s  %02d %s  %02d %s  %02d %s  %02d %s  %02d %s" % \
                (x, item[0], x+5, item[1], x+10, item[2], \
                x+15, item[3], x+20, item[4], x+25, item[5]))
            x += 1
        result = "\n".join(resl)
        use_template(self, "pwd.html", {
            'arg1' : "",
            'arg2' : "",
            'result' : result,
            })

application = webapp.WSGIApplication([
                                     ('/', MainPage),
                                     ('/qp/(.*)', QuanPin),
                                     ('/abc/(.*)', ShuangPinAbc),
                                     ('/abc', AbcPost),
                                     ('/ms/(.*)', ShuangPinMs),
                                     ('/wb/(.*)', Wubi),
                                     ('/pwd/(.*)', PwdTool),
                                     ('/pwd', PwdPost),
                                         ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
