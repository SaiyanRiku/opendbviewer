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

import gtk, gobject, pango

from appgui import panel, cellrenderers
from appgui.cellrenderers import cellrenderdbdata
from appgui.panel import queryresult
import dbconnector

(
	TAB_STRUCTURE,
	TAB_DATA,
	TAB_SQLCREATION,
) = range(3)

class TablePanelView(panel.Panel):

	gladeinfo = ('table_panel.glade', 'window')
	
	def __init__(self, parent, dbinterface, tablename, readonly):
		"""
            Initializes the table panel

            @param parent: the parent dialog
            @param dbinterface: the dbinterface instance
            @param tablename: the table inside the dbinterface
            @param readonly: the table is edited as readonly
		"""
		panel.Panel.__init__(self, parent, dbinterface.get_connection_display_name())

		self.db = dbinterface
		self.table = tablename
		self.readonly = readonly
		self.first_time = True

		# Add query result panel
		container = self.builder.get_object("eventbox_queryresult")
		self.queryresult_panel = queryresult.QueryResultPanelView(container)
		widget, name = self.queryresult_panel.get_panel()
		container.add(widget)
		
		# Connect signals
		widget = self.builder.get_object("button_clear")
		widget.connect("clicked", self.on_button_clear_clicked)
		
		widget = self.builder.get_object("entry_filter")
		widget.connect("activate", self.on_entry_filter_activate)
		
		widget = self.builder.get_object("button_refresh")
		widget.connect("clicked", self.on_button_refresh_clicked)

		widget = self.builder.get_object("notebook_table")
		widget.connect("switch-page", self.on_notebook_table_switch_page)

		dbworker = self.db.get_new_worker(self.queryresult_panel)
		dbworker.initialize()
		
		# Display the data structure in the treeview
		columns = dbworker.get_table_description(tablename)
		model = self.builder.get_object("liststore_structure")
		selectcol = []
		for col in columns:
			model.append([col[0], col[1], col[2], col[3], col[4]])
			selectcol.append(col[0])
		
		# Display the original creation script for the table
		sql = dbworker.get_table_sql_creation_script(tablename)
		textview = self.builder.get_object("textview_sqlcreationscript")
		buffer = gtk.TextBuffer()
		buffer.set_text(sql)
		textview.set_buffer(buffer)
		
		# Update display of the data
		#self.update_table_data(dbworker)

		dbworker.dispose()
		
		
	def on_button_clear_clicked(self, button):
		entry_filter = self.builder.get_object("entry_filter")
		entry_filter.set_text("")
		
		# Get the new data
		dbworker = self.db.get_new_worker(self.queryresult_panel)
		dbworker.initialize()

		self.update_table_data(dbworker)

		dbworker.dispose()
		
	def on_entry_filter_activate(self, entry):
		# Get the new data
		dbworker = self.db.get_new_worker(self.queryresult_panel)
		dbworker.initialize()

		self.update_table_data(dbworker)

		dbworker.dispose()
		
	def on_button_refresh_clicked(self, button):
		# Get the new data
		dbworker = self.db.get_new_worker(self.queryresult_panel)
		dbworker.initialize()

		self.update_table_data(dbworker)

		dbworker.dispose()

	def on_notebook_table_switch_page(self, notebook, page, page_num):
		
		if page_num == TAB_DATA and self.first_time:
			
			dbworker = self.db.get_new_worker(self.queryresult_panel)
			dbworker.initialize()

			self.update_table_data(dbworker)

			dbworker.dispose()
			
			self.first_time = False
			

	def update_table_data(self, dbworker):
		entry_filter = self.builder.get_object("entry_filter")
			
		text_filter = entry_filter.get_text()
		if text_filter == "":
			text_filter = None

		try:
			rowcount = dbworker.display_table_data(self.table, None, text_filter)
			self.queryresult_panel.show_results()
		except dbconnector.DbConnectorException, e:
			self.queryresult_panel.show_console()
		