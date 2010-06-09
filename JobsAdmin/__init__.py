
import gtk
from gobject import idle_add
from JobsAdmin.remote import RemoteJobService


class JobsAdminUI:

    def __init__(self):
        self.jobservice = RemoteJobService()
        self.active_job = None
        self.active_index = 0
        self.builder = gtk.Builder()
        self.builder.add_from_file('jobs-admin.ui')
        
        objects = [
            'win_main',
            'tv_jobs',
            'lbl_jobdesc',
            'img_status',
            'lbl_status',
            'btn_job_toggle',
            'img_job_toggle',
            'lbl_details',
            'btn_job_toggle',
            'btn_help',
            'btn_close',
            'lst_jobs',
        ]
        for obj in objects:
            self.__dict__[obj] = self.builder.get_object(obj)
        
        self.win_main.connect('destroy', gtk.main_quit)
        self.btn_close.connect('clicked', gtk.main_quit)
        
        self.tv_jobs_sel = self.tv_jobs.get_selection()
        self.tv_jobs.connect('cursor-changed', self.show_job_info)
        
        self.btn_job_toggle.connect('clicked', self.job_toggle)
    
    def load_jobs(self):
        self.lst_jobs.clear()
        for jobname, job in self.jobservice.get_all_jobs().iteritems():
            self.lst_jobs.append((jobname, 700 if job.running else 400))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
        # put the cursor on something to trigger show_job_details
        self.tv_jobs.set_cursor(self.active_index)
    
    def show_job_info(self, treeview):
        model, treeiter = self.tv_jobs_sel.get_selected()
        self.active_index = self.tv_jobs_sel.get_selected_rows()[1][0][0]
        jobname = self.lst_jobs.get_value(treeiter, 0)
        self.active_job = self.jobservice.jobs[jobname]
        # update some ui elements
        self.lbl_jobdesc.props.label = "<b>%s</b> - <i>%s</i>" % (
                jobname, self.active_job.description)
        self.set_running(self.active_job.running)
        self.set_details(self.active_job)

    def job_toggle(self, button):
        """
        Turn a job on or off.
        """
        self.set_waiting()
        # async callbacks so we don't appear to freeze
        def reply():
            self.set_running(self.active_job.running)
            self.set_waiting(False)
            self.load_jobs()
        def error(e):
            self.set_waiting(False)
        if self.active_job.running:
            self.active_job.stop(reply_handler=reply, error_handler=error)
        else:
            self.active_job.start(reply_handler=reply, error_handler=error)
        
    def set_waiting(self, waiting=True):
        """
        Disable the UI or re-enable it for an action.
        """
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH if waiting else gtk.gdk.ARROW)
        self.win_main.get_window().set_cursor(cursor)
        for obj in self.win_main.get_children():
            obj.props.sensitive = False if waiting else True
    
    def set_running(self, running):
        if running:
            self.img_status.set_from_stock(gtk.STOCK_MEDIA_PLAY,
                                           gtk.ICON_SIZE_BUTTON)
            self.lbl_status.props.label = "Running"
            self.img_job_toggle.set_from_stock(gtk.STOCK_MEDIA_STOP,
                                               gtk.ICON_SIZE_BUTTON)
            self.btn_job_toggle.props.label = "_Stop"
        else:
            self.img_status.set_from_stock(gtk.STOCK_MEDIA_STOP,
                                           gtk.ICON_SIZE_BUTTON)
            self.lbl_status.props.label = "Not running"
            self.img_job_toggle.set_from_stock(gtk.STOCK_EXECUTE,
                                               gtk.ICON_SIZE_BUTTON)
            self.btn_job_toggle.props.label = "_Start"
    
    def set_details(self, job):
        """
        Change the content of the "Details" expander to info about
        the set service.
        """
        txt = []
        starton = []
        stopon = []
        bk_names = {
            'sysv': 'System V',
            'upstart_0_6': 'Upstart (0.6)',
            'upstart_0_10': 'Upstart (0.10)',
        }
        if job.backend in bk_names:
            txt.append("Type: %s" % bk_names[job.backend])
        if job.backend == 'sysv':
            if job.starton:
                starton.append("on runlevels %s" % ", ".join(job.starton))
            if job.stopon:
                stopon.append("on runlevels %s" % ", ".join(job.stopon))
        else:
            if job.automatic:
                txt.append("Automatically started")
            else:
                txt.append("Manual mode")
        if starton: txt.append("Starts:\n\t%s" % "\n\t".join(starton))
        if stopon: txt.append("Stops:\n\t%s" % "\t".join(stopon))
        self.lbl_details.props.label = "\n\n".join(txt)
