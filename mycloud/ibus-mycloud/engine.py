# vim:set et sts=4 sw=4:
#
# ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import gobject
import pango
import enchant
import mycloud
import ibus
from ibus import keysyms
from ibus import modifier

class Engine(ibus.EngineBase):
    __dict = enchant.Dict("en")

    def __init__(self, bus, object_path):
        super(Engine, self).__init__(bus, object_path)
        self.__is_invalidate = False
        self.__preedit_string = u""
        self.__lookup_table = ibus.LookupTable()
        self.__prop_list = ibus.PropList()
        self.__prop_list.append(ibus.Property(u"test", icon = u"/usr/share/ibus-mycloud/icons/prop.svg"))

    def process_key_event(self, keyval, keycode, state):
        # ignore key release events
        is_press = ((state & modifier.RELEASE_MASK) == 0)
        if not is_press:
            return False
        # print "%s, kv=0x%x, kc=0x%x, st=0x%x" % (self, keyval, keycode, state)

        has_candidate = (self.__lookup_table.get_number_of_candidates() > 0)

        if self.__preedit_string:
            if keyval == keysyms.Return:
                self.__commit_string(self.__preedit_string)
            elif keyval == keysyms.Escape:
                if has_candidate:
                    self.__lookup_table.clean()
                    self.__update_lookup_table()
                self.__preedit_string = u""
                self.__update()
            elif keyval == keysyms.BackSpace:
                if has_candidate:
                    self.__lookup_table.clean()
                    self.__update_lookup_table()
                self.__preedit_string = self.__preedit_string[:-1]
                self.__invalidate()
            elif keyval == keysyms.space:
                if has_candidate:
                    self.__commit_string(self.__lookup_table.get_current_candidate().text)
                else:
                    preedit_len = len(self.__preedit_string)
                    attrs = ibus.AttrList()
                    self.__lookup_table.clean()
                    if preedit_len > 0:
                        res = mycloud.parsefunc(self.__preedit_string.encode("utf-8"), "172.16.55.240")
                        if res != "":
                            attrs.append(ibus.AttributeForeground(0xff0000, 0, preedit_len))
                            for item in res.split("\n"):
                                text = item.split("\t")[0]
                                if text:
                                    self.__lookup_table.append_candidate(ibus.Text(text))
                    self.__update_lookup_table()
                    self.__is_invalidate = False
            elif keyval >= keysyms._1 and keyval <= keysyms._9:
                if has_candidate:
                    index = keyval - keysyms._1
                    candidates = self.__lookup_table.get_candidates_in_current_page()
                    if index < len(candidates):
                        candidate = candidates[index].text
                        self.__commit_string(candidate)
                else:
                    if state & (modifier.CONTROL_MASK | modifier.ALT_MASK) == 0:
                        self.__preedit_string += unichr(keyval)
                        self.__invalidate()
            elif keyval == keysyms.minus:
                self.page_up()
            elif keyval == keysyms.equal:
                self.page_down()
            elif keyval == keysyms.Up:
                self.cursor_up()
            elif keyval == keysyms.Down:
                self.cursor_down()
            elif keyval == keysyms.Left or keyval == keysyms.Right:
                pass
            elif keyval in xrange(keysyms.a, keysyms.z + 1) or \
                keyval in xrange(keysyms.A, keysyms.Z + 1):
                if has_candidate:
                    self.__commit_string(self.__lookup_table.get_current_candidate().text)
                else:
                    pass
                if state & (modifier.CONTROL_MASK | modifier.ALT_MASK) == 0:
                    self.__preedit_string += unichr(keyval)
                    self.__invalidate()
            else:
                #print "blocked: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
                pass

            # block all input when preedit available
            return True
        else:
            if keyval in xrange(keysyms.a, keysyms.z + 1) or \
                keyval in xrange(keysyms.A, keysyms.Z + 1):
                if state & (modifier.CONTROL_MASK | modifier.ALT_MASK) == 0:
                    self.__preedit_string += unichr(keyval)
                    self.__invalidate()
                    return True
            elif keyval >= keysyms._1 and keyval <= keysyms._9:
                pass
            elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
                # this includes a-z, A-Z, 0-9 and all symbols
                # since we bypassed a-zA-Z0-9, we got all symbols
                res = mycloud.parsefunc(chr(keyval), "172.16.55.240")
                if res != "":
                    item = res.split("\n")
                    if item:
                        text = item[0].split("\t")
                        if text:
                            self.__commit_string(text[0])
                            return True
                else:
                    pass
            else:
                #print "ignored: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
                pass

            return False

    def __invalidate(self):
        if self.__is_invalidate:
            return
        self.__is_invalidate = True
        gobject.idle_add(self.__update, priority = gobject.PRIORITY_LOW)

    def page_up(self):
        if self.__lookup_table.page_up():
            self.page_up_lookup_table()
            return True
        return False

    def page_down(self):
        if self.__lookup_table.page_down():
            self.page_down_lookup_table()
            return True
        return False

    def cursor_up(self):
        if self.__lookup_table.cursor_up():
            self.cursor_up_lookup_table()
            return True
        return False

    def cursor_down(self):
        if self.__lookup_table.cursor_down():
            self.cursor_down_lookup_table()
            return True
        return False

    def __commit_string(self, text):
        self.commit_text(ibus.Text(text))
        self.__preedit_string = u""
        if self.__lookup_table.get_number_of_candidates() > 0:
            self.__lookup_table.clean()
            self.__update_lookup_table()
        self.__update()

    def __update(self):
        preedit_len = len(self.__preedit_string)
        attrs = ibus.AttrList()
        self.update_auxiliary_text(ibus.Text(self.__preedit_string, attrs), preedit_len > 0)
        attrs.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE, 0, preedit_len))
        self.update_preedit_text(ibus.Text(self.__preedit_string, attrs), preedit_len, preedit_len > 0)
        self.__is_invalidate = False

    def __update_lookup_table(self):
        visible = self.__lookup_table.get_number_of_candidates() > 0
        self.update_lookup_table(self.__lookup_table, visible)


    def focus_in(self):
        self.register_properties(self.__prop_list)

    def focus_out(self):
        pass

    def reset(self):
        pass

    def property_activate(self, prop_name):
        print "PropertyActivate(%s)" % prop_name

