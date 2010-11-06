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

from subprocess import Popen
import apport
import gtk
from JobsAdmin.gtk.extras import ExtraBase


class Extra(ExtraBase):
    
    def __init__(self, ui):
        self.ui = ui
        
        self.mi_apport = gtk.MenuItem(_("Report Service Problem"))
        self.mi_apport.connect('activate', self._report_problem)
        
        if not self.ui.menu_edit.extended:
            self.ui.menu_edit.append(gtk.SeparatorMenuItem())
            self.ui.menu_edit.extended = True
        self.ui.menu_edit.append(self.mi_apport)
    
    def update_ui(self):
        # don't run for protected jobs
        self.mi_apport.props.sensitive = not self.ui.active_job.protected
        
    def _report_problem(self, mi):
        dlg = gtk.MessageDialog(self.ui.win_main, gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL,
                _("Report a problem with {service}?").format(
                        service=self.ui.active_job.name))
        response = dlg.run()
        dlg.destroy()
        if response == gtk.RESPONSE_OK:
            run = ['apport-bug', '-f']
            if self.ui.active_job.pid:
                # when reporting specific processes we must be root
                run.insert(0, 'gksu')
                Popen([
                    'gksu', '-D', 'Apport',
                    '-m', _("Privileges are required to report this process."),
                    'apport-bug -f --pid {0}'.format(self.ui.active_job.pid)
                ])
            else:
                Popen(['apport-bug', '-f', '--package', self.ui.active_job.name])
