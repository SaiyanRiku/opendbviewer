#!/usr/bin/python
#
# main.py
# Copyright (C) Eric Beuque 2011 <eric.beuque@gmail.com>
# 
# OpenDBViewer is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# OpenDBViewer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require("2.0")
import sys, os, os.path

# Find out the location of openDBViewer's working directory, and insert it to sys.path
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "opendbviewer.py")):
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "opendbviewer.py")):
        basedir = cwd
        
print "Adding base %s" % basedir
sys.path.insert(0, basedir)

try:
	import sqlparse
	sqlparse.split('select * from foo; select * from bar;')
except ImportError, e:
	sqlparsedir = os.path.join(basedir, "..", "sqlparse-0.1.2")
	sys.path.insert(0, sqlparsedir)
	print "Adding sqlparse %s" % sqlparsedir	
	

# StartApp
def main():
    global app
    app = OpenDbViewer()
    gtk.main()

from app import xdg
import dbconnector
from appgui.panel import connection

from appgui import selectconnection

import gtk

class OpenDbViewer(object):

	def __init__(self):

		"""
			Initializes openDBViewer.
		"""
		(self.options, self.args) = self.get_options().parse_args()
		if self.options.UseDataDir:
			xdg.data_dirs.insert(1, self.options.UseDataDir)
			
		# Create the window
		builder = gtk.Builder()
		gladefile = xdg.get_data_path('ui/main.glade')
		builder.add_from_file(gladefile)
		builder.connect_signals({
			"on_menuitem_connect_activate" : self.on_menuitem_connect_activate
		})
		self.window = builder.get_object("window")
		self.window.show()
		self.window.connect("destroy", self.on_window_destroy)
	    
		self.notebook_connections = builder.get_object("notebook_connections")

		choosed = False;
		
		self.dirname = ""
		dialog = selectconnection.SelectConnection(self.dirname)
			
		if dialog.run() == gtk.RESPONSE_OK:
			connection_type = dialog.connection_type
			connection_string = dialog.connection_string
			connection_name = dialog.connection_name
			choosed = True
			self.dirname = dialog.dirname
		
		if choosed:
			self.open_database(connection_type, connection_name, connection_string)

	def get_options(self):
		"""
			Get the options for openDBViewer
		"""
		from optparse import OptionParser
		usage = "Usage: %prog [option...|uri]"
		p = OptionParser(usage=usage)

		# development and debug options
		p.add_option("--datadir", dest="UseDataDir", help="Set data directory")
		return p
	    
	def on_menuitem_connect_activate(self, menuitem):
		
		choosed = False;
		
		dialog = selectconnection.SelectConnection(self.dirname)
			
		if dialog.run() == gtk.RESPONSE_OK:
			connection_type = dialog.connection_type
			connection_name = dialog.connection_name
			connection_string = dialog.connection_string
			choosed = True
			self.dirname = dialog.dirname
		
		if choosed:
			self.open_database(connection_type, connection_name, connection_string)
	
	def open_database(self, connection_type, connection_name, connection_string):

		if connection_type == "SQLITE3":
			import dbconnector.sqlite3
			db = dbconnector.sqlite3.SQLite3(connection_name, connection_string)
		if connection_type == "Win32AdoDB":
			import dbconnector.win32adodb
			db = dbconnector.win32adodb.Win32AdoDb(connection_name, connection_string)
		
		
		# Create the panel and display it
		panel = connection.ConnectionPanelView(self.notebook_connections, db)
		
		# The the tab title
		box = gtk.HBox()
		tab_label = gtk.Label(db.get_connection_display_name())
		box.pack_start(tab_label, False, False)
		image = gtk.Image()
		image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
		button = gtk.Button()
		button.set_relief(gtk.RELIEF_NONE)
		button.set_image(image)
		# this reduces the size of the button
		style = gtk.RcStyle()
		style.xthickness = 0
		style.ythickness = 0
		button.modify_style(style)
		box.pack_start(button, False, False)
		box.show_all()
		
		# Add the panel
		widget, name = panel.get_panel()
		self.notebook_connections.append_page(widget, box)
		self.notebook_connections.show_all();
			
		# Connect the close button
		button.connect("clicked", self.on_button_tabclose_clicked, panel)
			
	def on_button_tabclose_clicked (self, button, panel):
		
		widget, name = panel.get_panel()
			
		# Remove the panel
		pagenum = self.notebook_connections.page_num(widget)
		self.notebook_connections.remove_page(pagenum)

	def on_window_destroy(self, window):
		gtk.main_quit()

if __name__ == "__main__":
	main()
