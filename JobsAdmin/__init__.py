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
from gobject import idle_add
from dbus.exceptions import DBusException
from JobsAdmin.extras import AllExtras
from JobsAdmin.remote import RemoteJobService
from JobsAdmin.settings import SettingsTable
from JobsAdmin.infobar import InfoManager

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
        self.waiting = False
        self.builder = gtk.Builder()
        
        # https://bugzilla.gnome.org/show_bug.cgi?id=574520
        self.builder.set_translation_domain('jobs-admin')
        
        try:
            self.builder.add_from_file('jobs-admin.ui')
        except:
            self.builder.add_from_file('/usr/share/jobs-admin/jobs-admin.ui')
        
        objects = [
            'act_job_start',
            'act_job_stop',
            'act_protected',
            'act_refresh',
            'cr_auto',
            'frm_settings',
            'lbl_job_mode',
            'lbl_job_starts',
            'lbl_job_status',
            'lbl_job_stops',
            'lbl_job_type',
            'lst_jobs',
            'menu_edit',
            'menu_help',
            'menu_jobs',
            'mi_about',
            'mi_quit',
            'tv_jobs',
            'vbox_right',
            'win_main',
        ]
        for obj in objects:
            self.__dict__[obj] = self.builder.get_object(obj)
        
        self.win_main.connect('destroy', gtk.main_quit)
        self.mi_quit.connect('activate', gtk.main_quit)
        
        self.tv_jobs_sel = self.tv_jobs.get_selection()
        self.tv_jobs.connect('cursor-changed', self.show_job_info)
        self.cr_auto.connect('toggled', self.auto_toggle)
        
        self.act_job_start.connect('activate', self.job_start)
        self.act_job_stop.connect('activate', self.job_stop)
        self.act_refresh.connect('activate', self.load_jobs)
        self.act_protected.connect('activate', self.set_protected)
        self.mi_about.connect('activate', self.show_about)
        
        self.lbl_job_starts.connect('activate-link', self.link_clicked)
        self.lbl_job_stops.connect('activate-link', self.link_clicked)
        
        self.infomanager = InfoManager(self.vbox_right)
        
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
                markup = "<b>{1}</b>\n<small>{0}</small>"
            else:
                markup = "{1}\n<small>{0}</small>"
            if job.description:
                markup = markup.format(jobname, job.description)
            else:
                markup = markup.format('', jobname)
            # update these if the liststore changes structure
            self.lst_jobs.append((jobname, markup, job.running,
                                  job.automatic, not job.protected))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
        # put the cursor on something to trigger show_job_info
        self.tv_jobs.set_cursor(self.active_index)
    
    def show_job_info(self, *args):
        """Update the UI with the currently selected job's info."""
        # we can't call on dbus while an async call is active, otherwise
        # this will block. also don't want to change active_index while
        # async calls are depending on it
        if self.waiting:
            return
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
        if job.backend == 'sysv':
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
        self.lbl_job_status.props.label = _("Running") if job.running else _("Not running")
        self.lbl_job_mode.props.label = _("Automatic") if job.automatic else _("Manual")
        # load settings
        self.show_settings()
        # clear the infobar
        if self.active_index != self.infomanager.active_index:
            self.infomanager.hide()
        # finally, tell our extras about the ui changes
        self.extras.update_ui()
    
    def auto_toggle(self, cr, path):
        self.active_index = int(path)
        row = self.lst_jobs[int(path)]
        job = self.jobservice.jobs[row[0]]
        if job.protected:
            return
        self.set_waiting()
        # handlers
        def reply():
            self.set_waiting(False)
            self.load_jobs()
            self.show_job_info()
            # infobar
            self.infomanager.hide()
            if job.automatic and not job.running:
                lbl = _("The job has been placed into automatic mode.\nWould you like to start it?")
                self.infomanager.show(self.active_index, lbl, _("_Start"), self.job_start)
            elif not job.automatic and job.running:
                lbl = _("The job has been placed into manual mode.\nWould you like to stop it?")
                self.infomanager.show(self.active_index, lbl, _("S_top"), self.job_stop)
        def error(e):
            self.set_waiting(False)
            self.show_job_info()
            if not 'DeniedByPolicy' in e._dbus_error_name:
                raise e
        # async call
        if job.automatic:
            job.disable(reply_handler=reply, error_handler=error)
        else:
            job.enable(reply_handler=reply, error_handler=error)

    def job_start(self, *args):
        """Start a job."""
        self.set_waiting()
        def reply():
            self.set_waiting(False)
            self.infomanager.hide()
            self.load_jobs()
        def error(e):
            if not 'DeniedByPolicy' in e._dbus_error_name:
                error = _("A problem has occurred:") + "\n\n\t" + e.get_dbus_message()
                if self.active_job.settings:
                    error += "\n\n" + _("Try changing the job settings and try again.")
                dlg = gtk.MessageDialog(self.win_main, gtk.DIALOG_MODAL,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, error)
                dlg.run()
                dlg.destroy()
            self.set_waiting(False)
        self.active_job.start(reply_handler=reply, error_handler=error)
    
    def job_stop(self, *args):
        """Stop a job."""
        self.set_waiting()
        def reply():
            self.set_waiting(False)
            self.infomanager.hide()
            self.load_jobs()
        def error(e):
            self.set_waiting(False)
            if not 'DeniedByPolicy' in e._dbus_error_name:
                raise e
        self.active_job.stop(reply_handler=reply, error_handler=error)
    
    def job_restart(self, *args):
        """Stop a job, then start it again."""
        self.job_stop()
        self.job_start()
    
    def show_settings(self):
        """Load the settings table for this job."""
        # only show for non-protected jobs with published settings
        if not self.active_job.settings or self.active_job.protected:
            self.frm_settings.hide_all()
            return
        tbl = SettingsTable(self.active_job)
        # apply button
        hbb = gtk.HButtonBox()
        hbb.props.layout_style = gtk.BUTTONBOX_END
        save = gtk.Button(stock='gtk-apply') 
        save.connect('clicked', self.apply_settings, tbl)
        hbb.pack_start(save)
        row = tbl.props.n_rows
        tbl.attach(hbb, 0, 2, row, row + 1)
        # remove the old table if present
        child = self.frm_settings.get_child()
        if child:
            self.frm_settings.remove(child)
            child.destroy()
        self.frm_settings.add(tbl)
        self.frm_settings.show_all()
    
    def apply_settings(self, button, tbl):
        """Call on the supplied SettingsTable to save settings and reload."""
        self.set_waiting()
        def reply():
            self.set_waiting(False)
            self.load_jobs()
            # infobar
            self.infomanager.hide()
            if self.active_job.running:
                lbl = _("The settings have been saved.\nRestart the job to apply these changes.")
                self.infomanager.show(self.active_index, lbl, _("_Restart"), self.job_restart)
        def error(e):
            self.set_waiting(False)
            if not 'DeniedByPolicy' in e._dbus_error_name:
                raise e
        tbl.apply_settings(reply, error)
        
    def set_waiting(self, waiting=True):
        """Disable the UI or re-enable it for an action."""
        self.waiting = waiting
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH if waiting else gtk.gdk.ARROW)
        self.win_main.get_window().set_cursor(cursor)
        for obj in self.win_main.get_children():
            obj.props.sensitive = not waiting
        
    def show_about(self, *args):
        dlg = gtk.AboutDialog()
        dlg.props.name = "jobs-admin"
        dlg.props.website = "https://launchpad.net/jobsadmin"
        try:
            from JobsAdmin.info import version, description
            dlg.props.version = version
            dlg.props.comments = description
        except: pass
        dlg.run()
        dlg.destroy()
    
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

