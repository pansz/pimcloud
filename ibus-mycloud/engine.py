# vim:set et sts=4 sw=4:
#
# ibus-mycloud - Personal Input Method Cloud Front-end for iBus
#
# Copyright (c) 2010-2012 Pan, Shi Zhu (pan dot shizhu at gmail dot com)
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
import mycloud
import ibus
from ibus import keysyms
from ibus import modifier

class Engine(ibus.EngineBase):

    def __init__(self, bus, object_path):
        super(Engine, self).__init__(bus, object_path)
        self.__is_invalidate = False
        self.__preedit_string = u""
        self.__lookup_table = ibus.LookupTable()
        self.__lookup_table.set_page_size(5)
        self.__prop_list = ibus.PropList()
        self.__prop_list.append(ibus.Property(u"test", icon = u"/usr/share/ibus-mycloud/icons/prop.svg"))
        self.__state = self.state_empty

    def process_key_event(self, keyval, keycode, state):
        try:
            is_valid = ((state & 
                    (modifier.RELEASE_MASK | modifier.CONTROL_MASK | modifier.ALT_MASK)) == 0)
            if not is_valid:
                # bypass KeyUp, Ctrl, Alt event
                return False

            # only procces KeyDown event
            ret = self.__state(keyval, keycode, state)
        except Exception, inst:
            print type(inst).__name__, inst
            return False
        return ret
    def state_is(self, target):
        return self.__state == target
    def state_transit(self, target):
        source = self.__state
        self.__state = target
        if source == self.state_empty:
            if target == self.state_input:
                self.__invalidate()
        elif source == self.state_input:
            if target == self.state_select:
                self.__update()
            elif target == self.state_empty:
                self.__preedit_string = u""
                self.__update()
        elif source == self.state_select:
            if target == self.state_empty:
                self.__preedit_string = u""
                self.__lookup_table.clean()
                self.__update_lookup_table()
                self.__update()
            elif target == self.state_input:
                self.__lookup_table.clean()
                self.__update_lookup_table()
                self.__invalidate()
        else:
            pass
    def state_empty(self, keyval, keycode, state):
        if keyval in xrange(keysyms.a, keysyms.z + 1):
            self.__preedit_string = unichr(keyval)
            self.state_transit(self.state_input)
            return True
        elif keyval in xrange(keysyms.A, keysyms.Z + 1):
            pass
        elif keyval >= keysyms._0 and keyval <= keysyms._9:
            pass
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            # this includes a-z, A-Z, 0-9 and all symbols
            # since we bypassed a-zA-Z0-9, we got all symbols
            res = self.__query_char(keyval)
            if res != "":
                self.__commit_string(res)
                return True
            else:
                pass
        else:
            #print "ignored: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass
        return False
    def cloud_query(self, pestr):
        res = mycloud.parsefunc(pestr.encode("utf-8"), "172.16.55.240")
        if res != "":
            preedit_len = len(pestr)
            for item in res.split("\n"):
                try:
                    text, index, hint = item.split("\t")
                    index = int(index)
                    if hint == "_":
                        display_text = text + pestr[index:]
                    else:
                        display_text = "%s%s(%s)" % \
                                (text, pestr[index:], hint)
                    ibt = ibus.Text(display_text)
                    ibt.index = index
                    ibt.commit_text = text
                    self.__lookup_table.append_candidate(ibt)
                except ValueError:
                    pass
    def state_input(self, keyval, keycode, state):
        if keyval == keysyms.Return:
            self.__commit_string(self.__preedit_string)
        elif keyval == keysyms.Escape:
            self.state_transit(self.state_empty)
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            self.__invalidate()
        elif keyval == keysyms.space:
            self.cloud_query(self.__preedit_string)
            if self.__lookup_table.get_number_of_candidates() > 0:
                self.__update_lookup_table()
                self.state_transit(self.state_select)
        elif keyval == keysyms.Left or keyval == keysyms.Right:
            pass
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            # This includes all visible ascii characters: [0x21, 0x7e]
            self.__preedit_string += unichr(keyval)
            self.__invalidate()
        else:
            #print "blocked: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass

        return True
    def sentence_update(self):
        self.__lookup_table.clean()
        self.cloud_query(self.__preedit_string)
        self.__update_lookup_table()
        if self.__lookup_table.get_number_of_candidates() > 0:
            self.state_transit(self.state_select)
            self.__invalidate()
        else:
            self.state_transit(self.state_input)
    def state_select(self, keyval, keycode, state):
        if keyval == keysyms.Return:
            self.__commit_string(self.__preedit_string)
        elif keyval == keysyms.Escape:
            self.state_transit(self.state_empty)
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            self.state_transit(self.state_input)
        elif keyval == keysyms.space:
            self.__commit_string(self.__lookup_table.get_current_candidate())
            if self.state_is(self.state_select):
                self.sentence_update()
        elif keyval >= keysyms._0 and keyval <= keysyms._9:
            index = keyval - keysyms._1
            if index < 0:
                index = 9
            candidates = self.__lookup_table.get_candidates_in_current_page()
            if index < len(candidates):
                self.__commit_string(candidates[index])
                if self.state_is(self.state_select):
                    self.sentence_update()
        elif keyval == keysyms.minus:
            self.page_up()
            self.__update()
        elif keyval == keysyms.equal:
            self.page_down()
            self.__update()
        elif keyval == keysyms.Left or keyval == keysyms.Right:
            pass
        elif keyval in xrange(keysyms.a, keysyms.z + 1) or \
            keyval in xrange(keysyms.A, keysyms.Z + 1):
            self.__commit_string(self.__lookup_table.get_current_candidate())
            if self.state_is(self.state_empty):
                return self.__state(keyval, keycode, state)
            else:
                self.sentence_update()
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            self.__commit_string(self.__lookup_table.get_current_candidate())
            if self.state_is(self.state_empty):
                return self.__state(keyval, keycode, state)
            else:
                self.sentence_update()
        else:
            #print "blocked: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass

        return True

    def __query_char(self, keyval):
        res = mycloud.parsefunc(chr(keyval), "172.16.55.240")
        if res != "":
            item = res.split("\n")
            if item:
                text = item[0].split("\t")
                if text:
                    return text[0]
        return ""
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
        if isinstance(text, ibus.Text):
            self.commit_text(ibus.Text(text.commit_text))
            self.__preedit_string = self.__preedit_string[text.index:]
            if self.__preedit_string == u"":
                self.state_transit(self.state_empty)
            else:
                self.update_auxiliary_text(ibus.Text(self.__preedit_string), True)
                self.state_transit(self.state_select)
        else:
            self.commit_text(ibus.Text(text))
            self.__preedit_string = u""
            self.state_transit(self.state_empty)

    def __update(self):
        if self.state_is(self.state_empty):
            ibt = ibus.Text("")
            self.update_auxiliary_text(ibt, False)
            self.update_preedit_text(ibt, 0, False)
            self.__is_invalidate = False
        elif self.state_is(self.state_input):
            preedit_len = len(self.__preedit_string)
            attrs = ibus.AttrList()
            ibt = ibus.Text(self.__preedit_string, attrs)
            self.update_auxiliary_text(ibt, True)
            attrs.append(ibus.AttributeUnderline(pango.UNDERLINE_LOW, 0, preedit_len))
            self.update_preedit_text(ibt, preedit_len, True)
            self.__is_invalidate = False
        elif self.state_is(self.state_select):
            self.update_auxiliary_text(ibus.Text(self.__preedit_string), True)
            ibt = self.__lookup_table.get_current_candidate()
            preedit_len = len(ibt.commit_text)
            self.update_preedit_text(ibus.Text(ibt.commit_text), preedit_len, True)
            self.__is_invalidate = False
        else:
            pass

    def __update_lookup_table(self):
        visible = self.__lookup_table.get_number_of_candidates() > 0
        self.update_lookup_table(self.__lookup_table, visible)

    def focus_in(self):
        self.register_properties(self.__prop_list)

    def focus_out(self):
        self.state_transit(self.state_empty)

    def reset(self):
        pass

    def property_activate(self, prop_name):
        print "PropertyActivate(%s)" % prop_name

