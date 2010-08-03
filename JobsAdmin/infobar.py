# This file is part of jobs-admin.
# Copyright 2010 Jacob Peddicord <jpeddicord@ubuntu.com>
#
# jobs-admin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jobs-admin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jobs-admin.  If not, see <http://www.gnu.org/licenses/>.

import gtk


class InfoManager:
    
    def __init__(self, container):
        self.container = container
        self.active_index = None
        self.ib = None
    
    def show(self, index, text, button=None, callback=None, msgtype=gtk.MESSAGE_QUESTION):
        self.hide()
        # set up the bar
        self.ib = gtk.InfoBar()
        self.active_index = index
        lbl = gtk.Label()
        lbl.set_markup(text)
        self.ib.get_content_area().pack_start(lbl)
        self.ib.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        if button:
            self.ib.add_button(button, gtk.RESPONSE_OK)
        self.ib.connect('response', self._callback, callback)
        self.ib.props.message_type = msgtype
        # pack and show
        self.container.pack_start(self.ib, expand=False)
        self.container.reorder_child(self.ib, 0)
        self.ib.show_all()
    
    def hide(self):
        if self.ib:
            self.active_index = None
            self.ib.destroy()
    
    def _callback(self, ib, response, callback):
        if response == gtk.RESPONSE_OK:
            return callback()
        self.hide()

