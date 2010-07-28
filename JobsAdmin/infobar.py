
import gtk


class InfoManager:
    
    def __init__(self, container):
        self.container = container
        self.active_index = None
        self.ib = None
    
    def show(self, index, text, button, callback, msgtype=gtk.MESSAGE_QUESTION):
        self.hide()
        # set up the bar
        self.ib = gtk.InfoBar()
        self.active_index = index
        self.ib.get_content_area().pack_start(gtk.Label(text))
        self.ib.add_button(button, gtk.RESPONSE_OK)
        self.ib.connect('response', callback)
        self.ib.props.message_type = msgtype
        # pack and show
        self.container.pack_start(self.ib, expand=False)
        self.container.reorder_child(self.ib, 0)
        self.ib.show_all()
    
    def hide(self):
        if self.ib:
            self.active_index = None
            self.ib.destroy()
        
