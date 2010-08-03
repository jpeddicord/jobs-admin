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

from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobsAdmin.overrides import is_protected, alt_description
from JobsAdmin.util import LANG, retry


class RemoteJobService:
    
    def __init__(self):
        self.jobs = {}
        self._connect()
        
    def _connect(self):
        self.bus = SystemBus()
        self.jobservice = Interface(self.bus.get_object(
                'com.ubuntu.JobService', '/com/ubuntu/JobService'),
                'com.ubuntu.JobService')
    
    def get_all_jobs(self, protect=True):
        self.jobs = {}
        def call(): return self.jobservice.GetAllJobs()
        alljobs = retry(self._connect, call)
        for job, path in alljobs:
            protected = is_protected(job)
            if not protect or not protected:
                self.jobs[job] = RemoteJob(job, path)
                self.jobs[job].protected = protected
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
        self.protected = False
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
        # override description
        if name == 'description':
            alt = alt_description(self.name)
            if alt:
                return alt
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
    
    def enable(self, reply_handler=None, error_handler=None):
        def call(): self.interface.SetAutomatic(True, timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        retry(self._connect, call)
        self.props = {}
    
    def disable(self, reply_handler=None, error_handler=None):
        def call(): self.interface.SetAutomatic(False, timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        retry(self._connect, call)
        self.props = {}
    
    def get_settings(self, reply_handler=None, error_handler=None):
        if '_settings' in self.props:
            return self.props['_settings']
        def call():
            self.props['_settings'] = self.interface.GetSettings(LANG,
                timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
            return self.props['_settings']
        return retry(self._connect, call)
        
    def set_settings(self, settings, reply_handler=None, error_handler=None):
        def call(): self.interface.SetSettings(settings, timeout=500,
                reply_handler=reply_handler, error_handler=error_handler)
        retry(self._connect, call)
        self.props = {}

