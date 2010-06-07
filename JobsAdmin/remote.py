
from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobsAdmin.protected import is_protected


class RemoteJobService:
    
    def __init__(self):
        self.jobs = {}
        self.bus = SystemBus()
        self.jobservice = Interface(
            self.bus.get_object('com.ubuntu.JobService', '/com/ubuntu/JobService'),
            'com.ubuntu.JobService'
        )
    
    def get_all_jobs(self):
        for job, path, running in self.jobservice.GetAllJobs():
            if not is_protected(job):
                self.jobs[job] = RemoteJob(job, path, running)
        return self.jobs
    

class RemoteJob:
    
    def __init__(self, name, path, running):
        self.name = name
        self.path = path
        self.running = running
        self.props = {}
        
        self.bus = SystemBus()
        self.obj = self.bus.get_object('com.ubuntu.JobService', path)
        self.interface = Interface(self.obj, 'com.ubuntu.JobService.Job')
    
    def __repr__(self):
        return "<RemoteJob %s>" % self.name
    
    def __getattr__(self, name):
        if not self.props:
            self.props = self.obj.GetAll('com.ubuntu.JobService.Job',
                                         dbus_interface=PROPERTIES_IFACE)
        return self.props[name]
    
    def start(self, reply_handler=None, error_handler=None):
        self.interface.Start(timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        # clear properties so we can get a fresh copy of the running state
        self.props = {}
    
    def stop(self, reply_handler=None, error_handler=None):
        self.interface.Stop(timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        self.props = {}
    
