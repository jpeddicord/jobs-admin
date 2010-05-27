
import gtk


class JobsAdminUI:

    def __init__(self, ui_file):
        self.builder = gtk.Builder()
        self.builder.add_from_file(ui_file)
        
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
        
        self.btn_close.connect('clicked', gtk.main_quit)
    
    def load_jobs(self):
        
    
    def run_settings_dialog(self, jobname):
        pass

