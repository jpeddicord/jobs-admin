
import gtk
from gobject import idle_add
from dbus.exceptions import DBusException
from JobsAdmin.extras import AllExtras
from JobsAdmin.remote import RemoteJobService
from JobsAdmin.settings import SettingsTable

BACKEND_NAMES = {
    'sysv': 'System V',
    'sysv_stb': 'System V (system-tools-backends)',
    'upstart_0_6': 'Upstart (0.6)',
    'upstart_0_10': 'Upstart (0.10)',
}


class JobsAdminUI:

    def __init__(self):
        self.jobservice = RemoteJobService()
        self.active_job = None
        self.active_index = 0
        self.builder = gtk.Builder()
        
        # https://bugzilla.gnome.org/show_bug.cgi?id=574520
        self.builder.set_translation_domain('jobs-admin')
        
        try:
            self.builder.add_from_file('jobs-admin.ui')
        except:
            self.builder.add_from_file('/usr/share/jobs-admin/jobs-admin.ui')
        
        objects = [
            'win_main',
            'tv_jobs',
            'btn_job_toggle',
            'img_job_toggle',
            'lbl_job_type',
            'lbl_job_starts',
            'lbl_job_stops',
            'act_job_start',
            'act_job_stop',
            'act_refresh',
            'act_protected',
            'menu_jobs',
            'menu_edit',
            'menu_help',
            'mi_quit',
            'frm_settings',
            'lst_jobs',
        ]
        for obj in objects:
            self.__dict__[obj] = self.builder.get_object(obj)
        
        self.win_main.connect('destroy', gtk.main_quit)
        self.mi_quit.connect('activate', gtk.main_quit)
        
        self.tv_jobs_sel = self.tv_jobs.get_selection()
        self.tv_jobs.connect('cursor-changed', self.show_job_info)
        
        self.act_job_start.connect('activate', self.job_toggle)
        self.act_job_stop.connect('activate', self.job_toggle)
        self.act_refresh.connect('activate', self.load_jobs)
        self.act_protected.connect('activate', self.set_protected)
        
        self.lbl_job_starts.connect('activate-link', self.link_clicked)
        self.lbl_job_stops.connect('activate-link', self.link_clicked)
        
        # this isn't a gtk property, it's for extras to use
        for m in (self.menu_jobs, self.menu_edit, self.menu_help):
            m.extended = False
        
        # load extras
        self.extras = AllExtras(self)
    
    def load_jobs(self, *args):
        """Load the job listing and populate the liststore."""
        self.lst_jobs.clear()
        protect = not self.act_protected.props.active
        for jobname, job in self.jobservice.get_all_jobs(protect).iteritems():
            weight = 700 if job.running else 400
            if job.running:
                markup = "<b>{0}</b>\n<small>{1}</small>"
            else:
                markup = "{0}\n<small>{1}</small>"
            markup = markup.format(jobname, job.description)
            # update these if the liststore changes structure
            self.lst_jobs.append((jobname, markup, job.running,
                                  job.automatic, not job.protected))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
        # put the cursor on something to trigger show_job_details
        self.tv_jobs.set_cursor(self.active_index)
    
    def show_job_info(self, treeview):
        """Update the UI with the currently selected job's info."""
        model, treeiter = self.tv_jobs_sel.get_selected()
        self.active_index = self.tv_jobs_sel.get_selected_rows()[1][0][0]
        jobname = self.lst_jobs.get_value(treeiter, 0)
        self.active_job = job = self.jobservice.jobs[jobname]
        # enable/disable some actions
        self.act_job_start.props.sensitive = not job.running and not job.protected
        self.act_job_stop.props.sensitive = job.running and not job.protected
        # backend type
        self.lbl_job_type.props.label = BACKEND_NAMES[job.backend] \
                if job.backend in BACKEND_NAMES else _("Unknown")
        # starton/stopon vary slightly by backend
        starton = []
        stopon = []
        if job.backend == 'sysv_stb':
            if job.starton:
                starton.append(_("on runlevels {list}").format(
                        list=", ".join(job.starton)))
            if job.stopon:
                stopon.append(_("on runlevels {list}").format(
                        list=", ".join(job.stopon)))
        elif job.backend == 'upstart_0_6':
            for mode, field in ((job.starton, starton), (job.stopon, stopon)):
                for item in mode:
                    if 'runlevel' in item:
                        field.append(item)
                    else:
                        action, jobname = item.split()
                        if jobname in self.jobservice.jobs:
                            jobname = "<a href='{0}'>{0}</a>".format(jobname)
                        field.append("on {0} {1}".format(action, jobname))
        self.lbl_job_starts.props.label = _("Unknown")
        self.lbl_job_stops.props.label = _("Unknown")
        if starton: self.lbl_job_starts.props.label = ", ".join(starton)
        if stopon: self.lbl_job_stops.props.label = ", ".join(stopon)
        # load settings
        self.show_settings()
        # finally, tell our extras about the ui changes
        self.extras.update_ui()

    def job_toggle(self, button):
        """Turn a job on or off."""
        self.set_waiting()
        # async callbacks so we don't appear to freeze
        def reply():
            self.set_waiting(False)
            self.load_jobs()
        def error(e):
            # ignore deniedbypolicy errors
            if not 'DeniedByPolicy' in e._dbus_error_name:
                error = _("A problem has occurred:") + "\n\n\t{0}".format(
                                e.get_dbus_message())
                if self.active_job.settings:
                    error += "\n\n" + _("Try changing the job settings and try again.")
                dlg = gtk.MessageDialog(self.win_main, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, error)
                dlg.run()
                dlg.destroy()
            self.set_waiting(False)
        if self.active_job.running:
            self.active_job.stop(reply_handler=reply, error_handler=error)
        else:
            self.active_job.start(reply_handler=reply, error_handler=error)
    
    def show_settings(self):
        """Load the settings table for this job."""
        if not self.active_job.settings or self.active_job.protected:
            self.frm_settings.hide_all()
            return
        tbl = SettingsTable(self.active_job)
        child = self.frm_settings.get_child()
        if child:
            self.frm_settings.remove(child)
        self.frm_settings.add(tbl)
        self.frm_settings.show_all()
        
    def set_waiting(self, waiting=True):
        """Disable the UI or re-enable it for an action."""
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH if waiting else gtk.gdk.ARROW)
        self.win_main.get_window().set_cursor(cursor)
        for obj in self.win_main.get_children():
            obj.props.sensitive = not waiting
    
    def set_protected(self, action):
        self.active_index = 0
        self.load_jobs()
    
    def link_clicked(self, label, uri):
        """Action for any link clicked to change to that job."""
        self.active_index = 0
        for job in self.lst_jobs:
            if uri == job[0]:
                break
            self.active_index += 1
        self.tv_jobs.set_cursor(self.active_index)
        return True
