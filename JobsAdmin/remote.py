
from dbus import SystemBus, Interface


class RemoteJobService:
    
    def __init__(self):
        self.jobs = []
        self.bus = SystemBus()
        self.jobservice = Interface(
            self.bus.get_object('com.ubuntu.JobService', '/com/ubuntu/JobService'),
            'com.ubuntu.JobService'
        )
    
    def get_all_jobs(self):
        for job, running in self.jobservice.GetAllJobs():
            self.jobs.append(RemoteJob(job, running))
        return self.jobs
    

class RemoteJob:
    
    def __init__(self, name, running):
        self.name = name
        self.running = running
    
    def __unicode__(self):
        return self.name
    
    
