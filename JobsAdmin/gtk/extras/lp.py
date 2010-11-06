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

from LaunchpadIntegration import add_items, set_sourcepackagename
from JobsAdmin.gtk.extras import ExtraBase


class Extra(ExtraBase):
    """Add Launchpad menu items to the Help menu."""
    
    def __init__(self, ui):
        set_sourcepackagename('jobs-admin')
        add_items(ui.menu_help, 0, False, True)
