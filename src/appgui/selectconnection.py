# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA

import gtk
from app import xdg

import os

(
   TAB_SQLITE,
   TAB_ADODB,
) = range(2)

class SelectConnection(object):

	def __init__(self, dirname):
		self.dirname = dirname
	
	def run(self):
			
		# Create the window
		builder = gtk.Builder()
		gladefile = xdg.get_data_path('ui/select_connection.glade')
		builder.add_from_file(gladefile)
		dialog = builder.get_object("dialog")

		filechooserbutton = builder.get_object("filechooserbutton_sqlitefile")
		filechooserbutton.set_current_folder(self.dirname)
		
		dialog.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
		
		result = dialog.run()
		if result == gtk.RESPONSE_OK:
			
			notebook = builder.get_object("notebook_selection")
			
			pagenum = notebook.get_current_page()
			if pagenum == TAB_SQLITE:
				filechooserbutton = builder.get_object("filechooserbutton_sqlitefile")
				self.connection_type = "SQLITE3"
				filename = filechooserbutton.get_filename()
				self.connection_name = os.path.basename(filename)
				self.connection_string = filename
				self.dirname =  os.path.dirname(filename)
				
			elif pagenum == TAB_ADODB:
				filechooserbutton = builder.get_object("filechooserbutton_adodbwin32_msaccessfile")
				self.connection_type = "Win32AdoDB"
				filename = filechooserbutton.get_filename()
				self.connection_name = os.path.basename(filename)
				self.connection_string = 'PROVIDER=Microsoft.Jet.OLEDB.4.0;DATA SOURCE=%s;' % filename
				self.dirname =  os.path.dirname(filename)
		
		dialog.destroy()
		
		return result
		