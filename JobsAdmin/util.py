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

from subprocess import Popen, PIPE
from locale import getdefaultlocale
from dbus.exceptions import DBusException

LANG = getdefaultlocale()[0]

def retry(connect, func):
    """Call a function, and re-try if there was a DBus connection issue."""
    try:
        return func()
    except DBusException, e:
        # only handle connection errors
        if 'org.freedesktop.DBus.Error' not in e._dbus_error_name:
            raise
        connect()
        return func()

def check_exec(check):
    p = Popen(['which', check], stdout=PIPE)
    return (p.wait() == 0)
