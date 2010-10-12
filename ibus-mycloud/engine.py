# vim:set et sts=4 sw=4:
# coding: utf-8
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
import mycloud
import ibus
import pango
from ibus import keysyms
from ibus import modifier
import json
import os

def load_config():
    dname = os.path.expanduser("~/.config/ibus")
    fname = dname+"/mycloud.json"
    try:
        fp = open(fname, "r")
        file_exists = True
    except Exception:
        file_exists = False
    if file_exists:
        try:
            ret = json.load(fp)
            fp.close()
            try:
                fp = open(fname, "w")
                json.dump(ret, fp, sort_keys=True, indent=4)
                fp.close()
            except Exception, inst:
                print type(inst).__name__, inst
            return ret
        except Exception:
            file_exists = False

    try:
        os.mkdirs(dname)
    except Exception:
        pass
    try:
        defaults = {
            u"host" : u"127.0.0.1",
            u"port" : 10007,
            u"pagesize" : 10,
            u"static" : True,
            }
        fp = open(fname, "w")
        json.dump(defaults, fp, sort_keys=True, indent=4)
        fp.close()
    except Exception, inst:
        print type(inst).__name__, inst
    return defaults

class Engine(ibus.EngineBase):

    def __init__(self, bus, object_path):
        super(Engine, self).__init__(bus, object_path)
        self.__is_invalidate = False
        self.__preedit_string = u""
        labels = []
        for i in ( "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"):
            labels.append(ibus.Text(unicode(i, "utf-8")))
        self.__lookup_table = ibus.LookupTable(labels=labels)
        self.conf = load_config()
        self.__lookup_table.set_page_size(self.conf.get(u"pagesize", 10))
        self.__prop_list = ibus.PropList()
        prop = ibus.Property(u"option", icon = u"/usr/share/ibus-mycloud/icons/prop.svg")
        if self.conf.get(u"static", True):
            prop.state = 0
        else:
            prop.state = 1
        self.__prop_list.append(prop)
        self.__host = self.conf.get(u"host", "127.0.0.1")
        self.__port = self.conf.get(u"port", 10007)
        self.set_static_mode(self.conf.get(u"static", True))

    def set_static_mode(self, static_mode):
        if (static_mode):
            self.state_empty = self.state_empty_static
            self.state_input = self.state_input_static
            self.state_select = self.state_select_static
        else:
            self.state_empty = self.state_empty_dynamic
            self.state_input = self.state_select_dynamic
            self.state_select = self.state_select_dynamic
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
        if source == self.state_empty_static:
            if target == self.state_input_static:
                self.__invalidate()
        elif source == self.state_input_static:
            if target == self.state_select_static:
                self.__update()
            elif target == self.state_empty_static:
                self.__preedit_string = u""
                self.__update()
        elif source == self.state_select_static:
            if target == self.state_empty_static:
                self.__preedit_string = u""
                self.__lookup_table.clean()
                self.__update_lookup_table()
                self.__update()
            elif target == self.state_input_static:
                self.__lookup_table.clean()
                self.__update_lookup_table()
                self.__invalidate()
        elif source == self.state_empty_dynamic:
            if target == self.state_select_dynamic:
                self.__invalidate()
        elif source == self.state_select_dynamic:
            if target == self.state_empty_dynamic:
                self.__preedit_string = u""
                self.__lookup_table.clean()
                self.__update_lookup_table()
                self.__update()
        else:
            pass
    def state_empty_dynamic(self, keyval, keycode, state):
        if keyval in xrange(keysyms.a, keysyms.z + 1):
            self.state_transit(self.state_select)
            return self.__state(keyval, keycode, state)
        elif keyval in xrange(keysyms.A, keysyms.Z + 1):
            pass
        elif keyval >= keysyms._0 and keyval <= keysyms._9:
            pass
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            # the above xrange() includes a-z, A-Z, 0-9 and all symbols
            # since we bypassed a-zA-Z0-9, we got all symbols
            res = self.__query_char(keyval)
            if res != "":
                self.__commit_string(unicode(res,"utf-8"))
                return True
            else:
                pass
        else:
            #print "ignored: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass
        return False
    def state_select_dynamic(self, keyval, keycode, state):
        if keyval == keysyms.Return:
            self.__commit_string(self.__preedit_string)
        elif keyval == keysyms.Escape:
            self.state_transit(self.state_empty)
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            if self.__preedit_string == u"":
                self.state_transit(self.state_empty)
            else:
                self.__lookup_table.clean()
                self.cloud_query(self.__preedit_string)
                self.__update_lookup_table()
                self.__invalidate()
        elif keyval == keysyms.space:
            self.__commit_string(self.__lookup_table.get_current_candidate())
            if self.state_is(self.state_select):
                self.__sentence_update()
        elif keyval == keysyms.Left or keyval == keysyms.Right:
            pass
        elif keyval >= keysyms._0 and keyval <= keysyms._9:
            index = keyval - keysyms._1
            if index < 0:
                index = 9
            self.__select_candidate(index)
        elif keyval == keysyms.minus:
            self.page_up()
            self.__update()
        elif keyval == keysyms.equal:
            self.page_down()
            self.__update()
        elif keyval == keysyms.Left or keyval == keysyms.Right:
            pass
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            # This includes all visible ascii characters: [0x21, 0x7e]
            self.__preedit_string += unichr(keyval)
            self.__lookup_table.clean()
            self.cloud_query(self.__preedit_string)
            self.__update_lookup_table()
            self.__invalidate()
        else:
            #print "blocked: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass

        return True
    def state_empty_static(self, keyval, keycode, state):
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
                self.__commit_string(unicode(res,"utf-8"))
                return True
            else:
                pass
        else:
            #print "ignored: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass
        return False
    def cloud_query_default(self, pestr):
        res = mycloud.parsefunc(pestr, self.__host, self.__port)
        preedit_len = len(pestr)
        if res != "":
            item = res.split("\n")[0]
            try:
                text, index, hint = item.split("\t")
                ibt = ibus.Text(text)
                ibt.index = index
                ibt.commit_text = text
                return ibt
            except ValueError:
                pass
        ibt = ibus.Text(pestr)
        ibt.index = preedit_len
        ibt.commit_text = pestr
        return ibt
    def cloud_query(self, pestr):
        res = mycloud.parsefunc(pestr, self.__host, self.__port)
        if res != "":
            preedit_len = len(pestr)
            for item in res.split("\n"):
                try:
                    text, index, hint = item.split("\t")
                    index = int(index)
                    if index < len(pestr):
                        display_text = text + ".."
                    elif hint == "_":
                        display_text = text
                    else:
                        display_text = text + hint
                    ibt = ibus.Text(display_text)
                    ibt.index = index
                    ibt.commit_text = text
                    attr = ibus.AttrList()
                    attr.append(ibus.AttributeForeground(pango.Color("Red"), 0, preedit_len))
                    self.__lookup_table.append_candidate(ibt)
                except ValueError:
                    pass
    def state_input_static(self, keyval, keycode, state):
        if keyval == keysyms.Return:
            self.__commit_string(self.__preedit_string)
        elif keyval == keysyms.Escape:
            self.state_transit(self.state_empty)
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            if self.__preedit_string == u"":
                self.state_transit(self.state_empty)
            else:
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
    def __sentence_update(self):
        self.__lookup_table.clean()
        self.cloud_query(self.__preedit_string)
        self.__update_lookup_table()
        if self.__lookup_table.get_number_of_candidates() > 0:
            self.state_transit(self.state_select)
            self.__invalidate()
        else:
            self.state_transit(self.state_input)
    def __select_candidate(self, index):
        candidates = self.__lookup_table.get_candidates_in_current_page()
        if index < len(candidates):
            self.__commit_string(candidates[index])
            if self.state_is(self.state_select):
                self.__sentence_update()
    def state_select_static(self, keyval, keycode, state):
        if keyval == keysyms.Return:
            self.__commit_string(self.__preedit_string)
        elif keyval == keysyms.Escape:
            self.state_transit(self.state_empty)
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            if self.__preedit_string == u"":
                self.state_transit(self.state_empty)
            else:
                self.state_transit(self.state_input)
        elif keyval == keysyms.space:
            self.__commit_string(self.__lookup_table.get_current_candidate())
            if self.state_is(self.state_select):
                self.__sentence_update()
        elif keyval >= keysyms._0 and keyval <= keysyms._9:
            index = keyval - keysyms._1
            if index < 0:
                index = 9
            self.__select_candidate(index)
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
                self.state_transit(self.state_input)
                return self.__state(keyval, keycode, state)
        elif keyval in xrange(keysyms.exclam, keysyms.asciitilde+1):
            self.__commit_string(self.__lookup_table.get_current_candidate())
            while not self.state_is(self.state_empty):
                ibt = self.cloud_query_default(self.__preedit_string)
                self.__commit_string(ibt)
            return self.__state(keyval, keycode, state)
        else:
            #print "blocked: keyval=0x%x, keycode=0x%x, state=0x%x" % (keyval, keycode, state)
            pass

        return True

    def __query_char(self, keyval):
        res = mycloud.parsefunc(chr(keyval), self.__host, self.__port)
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
        elif self.state_is(self.state_input_static):
            attr = ibus.AttrList()
            ibt = ibus.Text(self.__preedit_string, attr)
            self.update_auxiliary_text(ibt, True)
            preedit_len = len(self.__preedit_string)
            attr.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE, 0, preedit_len))
            self.update_preedit_text(ibt, preedit_len, True)
        elif self.state_is(self.state_select_static):
            self.update_auxiliary_text(ibus.Text(self.__preedit_string), True)
            ibt = self.__lookup_table.get_current_candidate()
            attr = ibus.AttrList()
            preedit_len = len(unicode(ibt.commit_text, "utf-8"))
            attr.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE, 0, preedit_len))
            self.update_preedit_text(ibus.Text(ibt.commit_text, attr), preedit_len, True)
        elif self.state_is(self.state_select_dynamic):
            self.update_auxiliary_text(ibus.Text(self.__preedit_string), True)
            ibt = self.__lookup_table.get_current_candidate()
            attr = ibus.AttrList()
            preedit_len = len(unicode(ibt.commit_text, "utf-8"))
            attr.append(ibus.AttributeUnderline(pango.UNDERLINE_SINGLE, 0, preedit_len))
            self.update_preedit_text(ibus.Text(ibt.commit_text, attr), preedit_len, True)
        else:
            pass
        self.__is_invalidate = False

    def __update_lookup_table(self):
        visible = self.__lookup_table.get_number_of_candidates() > 0
        self.update_lookup_table(self.__lookup_table, visible)

    def focus_in(self):
        self.register_properties(self.__prop_list)

    def focus_out(self):
        self.state_transit(self.state_empty)

    def reset(self):
        pass

    def property_activate(self, prop_name, prop_state):
        try:
            for item in self.__prop_list:
                self.state_transit(self.state_empty)
                if int(prop_state) == 1:
                    item.state = 0
                    item.icon = u"/usr/share/ibus-mycloud/icons/prop.svg"
                    self.set_static_mode(True)
                else:
                    item.state = 1
                    item.icon = u"/usr/share/ibus-mycloud/icons/prop1.svg"
                    self.set_static_mode(False)
                self.update_property(item)
                break
        except Exception, inst:
            print type(inst).__name__, inst

    def candidate_clicked(self, index, button, state):
        if state == 0 and button == 1:
            self.__select_candidate(index)
