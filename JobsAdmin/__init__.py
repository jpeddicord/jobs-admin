
import gtk
from remote import RemoteJobService


class JobsAdminUI:

    def __init__(self):
        self.jobservice = RemoteJobService()
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
    
    def load_jobs(self):
        for jobname, job in self.jobservice.get_all_jobs().iteritems():
            self.lst_jobs.append((jobname, 700 if job.running else 400))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
        # put the cursor on something to trigger show_job_details
        self.tv_jobs.set_cursor(0)
    
    def show_job_info(self, treeview):
        model, treeiter = self.tv_jobs_sel.get_selected()
        # we must have a selection at this point
        assert treeiter
        jobname = self.lst_jobs.get_value(treeiter, 0)
        job = self.jobservice.jobs[jobname]
        # update some ui elements
        self.lbl_jobdesc.props.label = "<b>%s</b> - <i>%s</i>" % (
                jobname, job.description)
        self.set_running(job.running)
        self.set_details(backend=job.backend)
        
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
    
    def set_details(self, automatic=False, starton=[], stopon=[], backend=None):
        txt = []
        if automatic:
            txt.append("Automatically started")
        else:
            txt.append("Manual mode")
        if starton: txt.append("Starts:\n\t%s" % '\n\t'.join(starton))
        if stopon: txt.append("Stops:\n\t%s" % '\t'.join(stopon))
        if backend: txt.append("Type: %s" % backend)
        self.lbl_details.props.label = '\n\n'.join(txt)
