# queryresult_panel.py
#
# Copyright (C) 2011 - Eric Beuque
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gtk, gobject, pango

from appgui import panel, cellrenderers
from appgui.cellrenderers import cellrenderdbdata

import dbconnector

class QueryResultPanelView(panel.Panel, dbconnector.DbActionUiRenderer):

	gladeinfo = ('queryresult_panel.glade', 'window')
	
	def __init__(self, parent):
		"""
            Initializes the table panel

            @param parent: the parent dialog
		"""
		panel.Panel.__init__(self, parent, "Query result")
		self.textbuffer_log = self.builder.get_object("textbuffer_log")
		
	def show_results(self):
		notebook = self.builder.get_object("notebook_queryresult")
		notebook.set_current_page(0)

	def show_console(self):
		notebook = self.builder.get_object("notebook_queryresult")
		notebook.set_current_page(1)

	def do_set_view_model(self, dbworker, rowid_desc, columns, liststore):

		use_rowid = False
		rowid_colname = None
		rowid_colidx = -1
		if rowid_desc != None:
			use_rowid = rowid_desc['use_rowid'] if rowid_desc.has_key('use_rowid') else False
			rowid_colname = rowid_desc['rowid_name'] if rowid_desc.has_key('rowid_name') else None
			rowid_colidx = rowid_desc['rowid_colidx'] if rowid_desc.has_key('rowid_colidx') else -1
		
		treeview = self.builder.get_object("treeview_data")
		model = treeview.get_model()

		# Delete all data in the model
		if model != None:
			model.clear()

		# Delete all column in the treeview
		for col in treeview.get_columns():
			treeview.remove_column(col)
		
		# Add column for rowid
		if use_rowid:
			cell_renderer = gtk.CellRendererText()
			cell_renderer.set_sensitive(False)
			cell_renderer.set_alignment(1, 0.5)
		
			treeviewcol = gtk.TreeViewColumn(rowid_colname, cell_renderer, text=rowid_colidx)
			treeview.append_column(treeviewcol)

		model_colidx = 0
		for col in columns:
			type_c = dbworker.connector.get_converted_column_type(col["type_code"])

			# Define the column
			cell_renderer = cellrenderdbdata.CellRendererDBData()
			#cell_renderer.set_property("ellipsize-set", True)
			#cell_renderer.set_property("ellipsize", pango.ELLIPSIZE_END)
			# Disable text multiline display
			#cell_renderer.set_fixed_height_from_font(1)
			celltype = cellrenderdbdata.DATATYPE_UNKNOW
			if type_c == dbconnector.DBC_FIELD_TYPE_INTEGER:
				celltype = cellrenderdbdata.DATATYPE_INTEGER
			if type_c == dbconnector.DBC_FIELD_TYPE_REAL:
				celltype = cellrenderdbdata.DATATYPE_REAL
			if type_c == dbconnector.DBC_FIELD_TYPE_TEXT:
				celltype = cellrenderdbdata.DATATYPE_TEXT
			if type_c == dbconnector.DBC_FIELD_TYPE_BLOB:
				celltype = cellrenderdbdata.DATATYPE_BLOB
			cell_renderer.set_data_type(celltype)
		
			label = gtk.Label(col["name"])
			label.set_use_underline(False)
			treeviewcol = gtk.TreeViewColumn(None, cell_renderer, data_text=col["model_colidx"])
			treeviewcol.set_widget(label)
			label.show_all()
			treeview.append_column(treeviewcol)

			# Set the model
			model = liststore
			treeview.set_model(model)

		return model

	def do_write_debug_log(self, dbworker, text):
		iter = self.textbuffer_log.get_start_iter()
		self.textbuffer_log.insert(iter, text)