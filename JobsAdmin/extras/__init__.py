

class ExtraBase:
    def __init__(self, ui):
        pass
    def update_ui(self):
        pass

class AllExtras(ExtraBase):

    def __init__(self, ui):
        self.ui = ui
        self.extras = []
        for extra in ('apport', 'packagekit'):
            mod = __import__('JobsAdmin.extras.' + extra, fromlist=['Extra'])
            self.extras.append(mod.Extra(self.ui))
    
    def update_ui(self):
        for extra in self.extras:
            extra.update_ui()
