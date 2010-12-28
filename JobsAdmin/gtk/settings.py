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

from subprocess import Popen, PIPE
from pwd import getpwall
from grp import getgrall
import gtk
from JobsAdmin.util import check_exec


class SettingsTable(gtk.Table):
    
    def __init__(self, job, index, infomanager):
        self.job = job
        self.index = index
        self.infomanager = infomanager
        self.settings = job.get_settings()
        self.widgets = {}
        self.warnings = []
        gtk.Table.__init__(self, len(self.settings) + 1, 2)
        self.props.row_spacing = 5
        self.props.column_spacing = 10
        self.props.border_width = 5
        
        # clear it out first
        for w in self:
            self.remove(w)
        
        row = 0
        # add the settings fields
        for name, stype, desc, val, vals, constrs in self.settings:
            # display varies by type
            if stype == 'bool':
                widget = gtk.CheckButton(desc)
                widget.props.active = (val == 'true')
            
            elif stype == 'int':
                imin = constrs['min'] if 'min' in constrs else -65535
                imax = constrs['max'] if 'max' in constrs else 65535
                adj = gtk.Adjustment(int(val),
                        float(imin), float(imax), 1)
                widget = gtk.SpinButton(adj)
            
            elif stype == 'float':
                imin = constrs['min'] if 'min' in constrs else -65535
                imax = constrs['max'] if 'max' in constrs else 65535
                adj = gtk.Adjustment(float(val),
                        float(imin), float(imax), 0.1)
                widget = gtk.SpinButton(adj, digits=1)
            
            elif stype == 'choice':
                lst = gtk.ListStore(str, str)
                widget = gtk.ComboBox(lst)
                cell = gtk.CellRendererText()
                widget.pack_start(cell)
                widget.add_attribute(cell, 'text', 1)
                index = 0
                for vname, vdesc in vals:
                    lst.append((vname, vdesc))
                    if vname == val:
                        widget.props.active = index
                    index += 1
            
            elif stype == 'file' or stype == 'dir':
                # gtk file choosers don't work well for non-existent files
                if 'exist' in constrs and constrs['exists'] == 'false':
                    widget = gtk.Entry()
                    widget.props.text = val
                else:
                    if stype == 'file':
                        widget = gtk.FileChooserButton("Choose a file")
                        widget.props.action = gtk.FILE_CHOOSER_ACTION_OPEN
                    else:
                        widget = gtk.FileChooserButton("Choose a folder")
                        widget.props.action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
                    widget.set_filename(val)
            
            elif stype == 'user' or stype == 'group':
                lst = gtk.ListStore(int, str)
                widget = gtk.ComboBox(lst)
                cell = gtk.CellRendererText()
                widget.pack_start(cell)
                widget.add_attribute(cell, 'text', 1)
                index = 0
                if stype == 'user':
                    for u in sorted(getpwall()):
                        lst.append((u.pw_uid, u.pw_name))
                        # user names & ids will never clash
                        if val == str(u.pw_uid) or val == u.pw_name:
                            widget.props.active = index
                        index += 1
                else:
                    for g in sorted(getgrall()):
                        lst.append((g.gr_gid, g.gr_name))
                        # same as above w/ users
                        if val == str(g.gr_gid) or val == g.gr_name:
                            widget.props.active = index
                        index += 1
            
            elif stype == 'exec':
                widget = gtk.Button(_("_Unavailable"))
                missing = None
                # static value
                if val:
                    # check for existence
                    check = val.split()[0]
                    if not check_exec(check):
                        widget.props.sensitive = False
                        missing = check
                    else:
                        widget.connect('clicked', run_action, val)
                        widget.props.label = _("Launch")
                # fallback list
                else:
                    for vname, vdesc in vals:
                        # check to see if it exists
                        check = vname.split()[0]
                        p = Popen(['which', check], stdout=PIPE)
                        if not check_exec(check):
                            missing = check
                            continue
                        # take the first valid action
                        widget.connect('clicked', run_action, vname)
                        widget.props.label = vdesc
                        missing = None
                        break
                if missing:
                    # this is temporary until we can properly search packages.
                    self.warnings.append(
                        _("An application is not installed. {search_link}").format(
                            search_link="<a href=\"http://packages.ubuntu.com/search?searchon=contents&amp;mode=exactfilename&amp;keywords={0}\">{1}</a>".format(
                                check, _("Search online"))))
                        
            elif stype == 'label':
                widget = gtk.Label()
                widget.props.xalign = 0
                widget.set_markup(desc)
            
            # use a string for 'str' and all other unknowns
            else:
                widget = gtk.Entry()
                widget.props.text = val
            
            # checkboxes & labels don't need extra labels
            if stype == 'bool' or stype == 'label':
                self.attach(widget, 0, 2, row, row + 1)
            # but the others don't; let's add them
            else:
                lbl = gtk.Label(desc + ":")
                lbl.props.xalign = 0
                self.attach(lbl, 0, 1, row, row + 1)
                self.attach(widget, 1, 2, row, row + 1)
            
            row += 1
            self.widgets[name] = widget
        
        self.show_all()
        
        if self.warnings:
            self.show_warnings()
            
    def apply_settings(self, reply, error):
        newsettings = {}
        for setting in self.settings:
            widget = self.widgets[setting[0]]
            # grab the value based on type
            if setting[1] == 'bool':
                value = 'true' if widget.props.active else 'false'
            elif setting[1] == 'int':
                value = int(widget.props.value)
            elif setting[1] == 'float':
                value = widget.props.value
            elif setting[1] == 'choice':
                value = widget.get_model()[widget.props.active][0]
            elif setting[1] == 'file' or setting[1] == 'dir':
                if 'exist' in setting[5] and setting[5]['exist'] == 'false':
                    value = widget.props.text
                else:
                    value = widget.get_filename()
                    if value == None:
                        value = ''
            elif setting[1] == 'user' or setting[1] == 'group':
                row = widget.get_model()[widget.props.active]
                if 'useid' in setting[5] and setting[5]['useid'] == 'true':
                    value = row[0]
                else:
                    value = row[1]
            elif setting[1] == 'label' or setting[1] == 'exec' or setting[1] == 'open':
                continue
            else: # str and unknowns
                value = widget.props.text
            # only send it if changed
            if value != setting[3]:
                newsettings[setting[0]] = str(value)
        self.job.set_settings(newsettings,
                              reply_handler=reply, error_handler=error)
    
    def show_warnings(self):
        text = _("Some settings are not available:")
        text += "\n" + "\n".join(self.warnings)
        self.infomanager.show(self.index, text, msgtype=gtk.MESSAGE_WARNING)


def run_action(button, action):
    Popen(action, shell=True)
