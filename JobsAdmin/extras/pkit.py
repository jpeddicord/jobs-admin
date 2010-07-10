
from dbus import SystemBus, Interface
import gtk
from JobsAdmin.extras import ExtraBase

# this will end here if PK is not installed
from packagekit.gtkwidgets import PackageKitInstaller

#TODO: *sigh* packagekit is also broken in maverick, but in a different way.
# see LP #603711
assert False

class Extra(ExtraBase):
    
    def __init__(self, ui):
        self.ui = ui
        
        self.bus = SystemBus()
        self.pkit = Interface(self.bus.get_object(
                'org.freedesktop.PackageKit', '/org/freedesktop/PackageKit'),
                'org.freedesktop.PackageKit')
        
        self.mi_uninstall = gtk.MenuItem("Uninstall Package")
        self.mi_uninstall.connect('activate', self._uninstall_package)
        if not self.ui.menu_edit.extended:
            self.ui.menu_edit.append(gtk.SeparatorMenuItem())
            self.ui.menu_edit.extended = True
        self.ui.menu_edit.append(self.mi_uninstall)
        
    def _uninstall_package(self, mi):
        self.ui.set_waiting()
        def search_cb(info, package_id, summary):
            pki = PackageKitInstaller(parent=self.ui.win_main)
            pki.remove_by_name((package_id.split(';')[0],))
            self.ui.set_waiting(False)
        tid = self.pkit.GetTid()
        txn = Interface(self.bus.get_object('org.freedesktop.PackageKit', tid),
                'org.freedesktop.PackageKit.Transaction')
        txn.connect_to_signal('Package', search_cb)
        txn.SearchFiles('none', [self.ui.active_job.file])
        
