
from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobsAdmin.protected import is_protected
from JobsAdmin.util import retry


class RemoteJobService:
    
    def __init__(self):
        self.jobs = {}
        self._connect()
        
    def _connect(self):
        self.bus = SystemBus()
        self.jobservice = Interface(self.bus.get_object(
                'com.ubuntu.JobService', '/com/ubuntu/JobService'),
                'com.ubuntu.JobService')
    
    def get_all_jobs(self):
        def call(): return self.jobservice.GetAllJobs()
        alljobs = retry(self._connect, call)
        for job, path in alljobs:
            if not is_protected(job):
                self.jobs[job] = RemoteJob(job, path)
        return self.jobs
    

class RemoteJob:
    """
    A proxy object for a single job. DBus properties are accessible via
    regular Python properties.
    """
    
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.props = {}
        self._connect()
        
    def _connect(self):
        self.bus = SystemBus()
        self.obj = self.bus.get_object('com.ubuntu.JobService', self.path)
        self.interface = Interface(self.obj, 'com.ubuntu.JobService.Job')
    
    def __getattr__(self, name):
        if not self.props:
            def call():
                self.props = self.obj.GetAll('com.ubuntu.JobService.Job',
                        dbus_interface=PROPERTIES_IFACE)
            retry(self._connect, call)
        return self.props[name]
    
    def start(self, reply_handler=None, error_handler=None):
        def call(): self.interface.Start(timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        retry(self._connect, call)
        self.props = {} # states may change
    
    def stop(self, reply_handler=None, error_handler=None):
        def call(): self.interface.Stop(timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        retry(self._connect, call)
        self.props = {}
    
    def get_settings(self):
        def call(): return self.interface.GetSettings()
        return retry(self._connect, call)
        
    def set_settings(self, settings):
        def call(): self.interface.SetSettings(settings)
        retry(self._connect, call)
        
