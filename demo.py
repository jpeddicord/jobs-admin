#!/usr/bin/python

import gtk

b = gtk.Builder()
b.add_from_file("mockup.ui")
w = b.get_object("win_main")
d = b.get_object("dlg_settings")

w.show_all()
d.show_all()

gtk.main()
