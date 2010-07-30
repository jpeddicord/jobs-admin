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


class ContextMenu(gtk.Menu):
    
    def __init__(self, act_start, act_stop):
        gtk.Menu.__init__(self)
        mi_start = act_start.create_menu_item()
        mi_stop = act_stop.create_menu_item()
        self.add(mi_start)
        self.add(mi_stop)
    
    def popup(self, widget, event):
        gtk.Menu.popup(self, None, None, None, event.button, event.time)
