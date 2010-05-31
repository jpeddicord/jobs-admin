
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
        self.tv_jobs.connect('cursor-changed', self.show_job_details)
    
    def load_jobs(self):
        for jobname, job in self.jobservice.get_all_jobs().iteritems():
            self.lst_jobs.append((jobname, 700 if job.running else 400))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
        # put the cursor on something to trigger show_job_details
        self.tv_jobs.set_cursor(0)
    
    def show_job_details(self, treeview):
        model, treeiter = self.tv_jobs_sel.get_selected()
        # we must have a selection at this point
        assert treeiter
        jobname = self.lst_jobs.get_value(treeiter, 0)
        job = self.jobservice.jobs[jobname]
        # update some ui elements
        self.lbl_jobdesc.props.label = "<b>%s</b> - <i>%s</i>" % (
                jobname, job.description)
        if job.running:
            self.lbl_status.props.label = "Running"
        else:
            self.lbl_status.props.label = "Not running"

