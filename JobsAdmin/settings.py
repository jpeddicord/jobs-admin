
import gtk


class SettingsDialog(gtk.Dialog):
    
    def __init__(self, job, parent=None):
        gtk.Dialog.__init__(self, "Job Settings", parent, gtk.DIALOG_MODAL, (
            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
        ))
        self.job = job
        self.vbox.props.spacing = 5
        self.props.border_width = 5
        
        # add the settings fields
        for name, details in self.job.get_settings().iteritems():
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
                widget = gtk.Entry()
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
                widget.show()
                self.vbox.pack_start(widget, False)
            # but the others don't; let's add them
            else:
                hbox = gtk.HBox()
                hbox.props.spacing = 10
                lbl = gtk.Label("{0}:".format(details[1]))
                lbl.props.xalign = 0
                hbox.pack_start(lbl)
                hbox.pack_start(widget)
                hbox.show_all()
                self.vbox.pack_start(hbox, False)
            
    def apply_settings(self):
        pass
