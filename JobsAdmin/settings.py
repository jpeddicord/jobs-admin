
import gtk


class SettingsDialog(gtk.Dialog):
    
    def __init__(self, job, settings, parent=None):
        gtk.Dialog.__init__(self, _("Job Settings"), parent, gtk.DIALOG_MODAL, (
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
        ))
        # dialog actions
        self.connect('response', self.apply_settings)
        self.job = job
        self.settings = settings
        self.widgets = {}
        # use a table layout
        self.table = gtk.Table(len(self.settings), 2)
        self.table.props.row_spacing = 5
        self.table.props.column_spacing = 10
        self.table.props.border_width = 5
        
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
            
            elif stype == 'file':
                widget = gtk.FileChooserButton("Choose a file")
            
            elif stype == 'dir':
                widget = gtk.FileChooserButton("Choose a folder")
            
            # use a string for 'str' and all other unknowns
            else:
                widget = gtk.Entry()
                widget.props.text = val
            
            # checkboxes already have labels
            if stype == 'bool':
                self.table.attach(widget, 0, 2, row, row + 1)
            # but the others don't; let's add them
            else:
                lbl = gtk.Label("{0}:".format(desc))
                lbl.props.xalign = 0
                self.table.attach(lbl, 0, 1, row, row + 1)
                self.table.attach(widget, 1, 2, row, row + 1)
            
            row += 1
            self.widgets[name] = widget
        
        self.vbox.pack_start(self.table)
        self.vbox.show_all()
            
    def apply_settings(self, dialog, response):
        if response != gtk.RESPONSE_ACCEPT:
            return
        newsettings = {}
        for setting in self.settings:
            widget = self.widgets[setting[0]]
            # grab the value based on type
            if setting[1] == 'bool':
                value = 'true' if widget.props.active else 'false'
            elif setting[1] == 'int':
                value = str(int(widget.props.value))
            elif setting[1] == 'float':
                value = str(widget.props.value)
            elif setting[1] == 'choice':
                value = widget.get_model()[widget.props.active][0]
            elif setting[1] == 'file' or setting[1] == 'dir':
                value = "unknown" #TODO
            else: # str and unknowns
                value = widget.props.text
            # only send it if changed
            if value != setting[3]:
                newsettings[setting[0]] = value
        self.job.set_settings(newsettings)

