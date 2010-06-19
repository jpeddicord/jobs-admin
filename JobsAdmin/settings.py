
import gtk


class SettingsDialog(gtk.Dialog):
    
    def __init__(self, job, parent=None):
        gtk.Dialog.__init__(self, "Job Settings", parent, gtk.DIALOG_MODAL, (
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
        ))
        self.job = job
        settings = self.job.get_settings()
        self.table = gtk.Table(len(settings), 2)
        self.table.props.row_spacing = 5
        self.table.props.column_spacing = 10
        self.table.props.border_width = 5
        row = 0
        
        # add the settings fields
        for name, details in settings.iteritems():
            if details[0] == 'bool':
                widget = gtk.CheckButton(details[1])
            elif details[0] == 'int':
                widget = gtk.HBox()
                lbl = gtk.Label("{0}:".format(details[1]))
                widget.pack_start(lbl)
                sb = gtk.SpinButton()
                widget.pack_start(sb)
            elif details[0] == 'float':
                widget = gtk.SpinButton()
            elif details[0] == 'str':
                widget = gtk.ComboBoxEntry()
            elif details[0] == 'choice':
                lst = gtk.ListStore(str)
                widget = gtk.ComboBox(lst)
                cell = gtk.CellRendererText()
                widget.pack_start(cell)
                widget.add_attribute(cell, 'text', 0)
                for vname, vdesc in details[3]:
                    lst.append((vdesc,))
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
        
        self.vbox.pack_start(self.table)
        self.vbox.show_all()
            
    def apply_settings(self):
        pass
