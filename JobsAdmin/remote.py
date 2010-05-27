
from dbus import SystemBus, Interface


class RemoteJobService(self):
    
    def __init__(self):
        self.bus = SystemBus()
        self.jobservice = Interface(
            self.bus.get_object('com.ubuntu.JobService', '/com/ubuntu/JobService'),
            'com.ubuntu.JobService'
        )
    
    def get_all_jobs(self):
        #TODO: return a list of RemoteJob objects
        self.jobservice.GetAllJobs()
    

class RemoteJob:
    
    def __init__(self):
        pass
    
    
