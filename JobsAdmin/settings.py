
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
        for name, details in self.settings.iteritems():
            # display varies by type
            if details[0] == 'bool':
                widget = gtk.CheckButton(details[1])
                widget.props.active = (details[2] == 'true')
            
            elif details[0] == 'int':
                imin = details[4]['min'] if 'min' in details[4] else -65535
                imax = details[4]['max'] if 'max' in details[4] else 65535
                adj = gtk.Adjustment(int(details[2]),
                        float(imin), float(imax), 1)
                widget = gtk.SpinButton(adj)
            
            elif details[0] == 'float':
                imin = details[4]['min'] if 'min' in details[4] else -65535
                imax = details[4]['max'] if 'max' in details[4] else 65535
                adj = gtk.Adjustment(float(details[2]),
                        float(imin), float(imax), 0.1)
                widget = gtk.SpinButton(adj, digits=1)
            
            elif details[0] == 'str':
                widget = gtk.Entry()
                widget.props.text = details[2]
            
            elif details[0] == 'choice':
                lst = gtk.ListStore(str, str)
                widget = gtk.ComboBox(lst)
                cell = gtk.CellRendererText()
                widget.pack_start(cell)
                widget.add_attribute(cell, 'text', 1)
                index = 0
                for vname, vdesc in details[3]:
                    lst.append((vname, vdesc))
                    if vname == details[2]:
                        widget.props.active = index
                    index += 1
            
            elif details[0] == 'file':
                widget = gtk.FileChooserButton("Choose a file")
            
            elif details[0] == 'dir':
                widget = gtk.FileChooserButton("Choose a folder")
            
            # checkboxes already have labels
            if details[0] == 'bool':
                self.table.attach(widget, 0, 2, row, row + 1)
            # but the others don't; let's add them
            else:
                lbl = gtk.Label("{0}:".format(details[1]))
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
        for name, details in self.settings.iteritems():
            widget = self.widgets[name]
            # grab the value based on type
            if details[0] == 'bool':
                value = 'true' if widget.props.active else 'false'
            elif details[0] == 'int':
                value = str(int(widget.props.value))
            elif details[0] == 'float':
                value = str(widget.props.value)
            elif details[0] == 'str':
                value = widget.props.text
            elif details[0] == 'choice':
                value = widget.get_model()[widget.props.active][0]
            elif details[0] == 'file' or details[0] == 'dir':
                value = "unknown" #TODO
            # only send it if changed
            if value != details[2]:
                newsettings[name] = value
        self.job.set_settings(newsettings)
