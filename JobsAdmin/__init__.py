
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
    
    def load_jobs(self):
        for job in self.jobservice.get_all_jobs():
            self.lst_jobs.append((job.name, job.running))
        self.lst_jobs.set_sort_column_id(0, gtk.SORT_ASCENDING)
    
    def run_settings_dialog(self, jobname):
        pass

