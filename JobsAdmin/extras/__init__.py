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


class ExtraBase:
    def __init__(self, ui):
        pass
    def update_ui(self):
        pass

class AllExtras(ExtraBase):

    def __init__(self, ui):
        self.ui = ui
        self.extras = []
        for extra in ('apportreport', 'pkit'):
            try:
                mod = __import__('JobsAdmin.extras.' + extra, fromlist=['Extra'])
                self.extras.append(mod.Extra(self.ui))
            except Exception, e:
                print e
    
    def update_ui(self):
        for extra in self.extras:
            extra.update_ui()
