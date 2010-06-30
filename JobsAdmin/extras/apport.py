
from subprocess import Popen
import gtk
from JobsAdmin.extras import ExtraBase

# ensures this only runs on systems with apport
import apport


class Extra(ExtraBase):
    
    def __init__(self, ui):
        self.ui = ui
        
        self.mi_apport = gtk.MenuItem("Report Service Problem")
        self.mi_apport.connect('activate', self.report_problem)
        
        if not self.ui.menu_edit.extended:
            self.ui.menu_edit.append(gtk.SeparatorMenuItem())
            self.ui.menu_edit.extended = True
        self.ui.menu_edit.append(self.mi_apport)
        
    def report_problem(self, mi):
        dlg = gtk.MessageDialog(self.ui.win_main, gtk.DIALOG_MODAL,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL,
                "Report a problem with {service}?".format(
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
                    '-m', "Privileges are required to report this process.",
                    'apport-bug -f --pid {0}'.format(self.ui.active_job.pid)
                ])
            else:
                Popen(['apport-bug', '-f', '--package', self.ui.active_job.name])
