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

import gtk

from appgui import panel
from appgui.panel import table
from appgui.panel import worksheet

(
   LABEL_COLUMN,
   TYPE_COLUMN,
) = range(2)

(
   TYPE_CATEGORY_NAME,
   TYPE_ITEM_TABLE,
   TYPE_ITEM_SYSTEMTABLE,
   TYPE_ITEM_VIEW,
   TYPE_ITEM_TRIGGER,
) = range(5)

class ConnectionPanelView(panel.Panel):

	gladeinfo = ('connection_panel.glade', 'window')
	
	def __init__(self, parent, dbinterface):
		"""
            Initializes the connection panel

            @param parent: the parent dialog
            @param dbinterface: the dbinterface instance
		"""
		panel.Panel.__init__(self, parent, dbinterface.get_connection_display_name())

		# Get table
		self.notebook_structureitems = self.builder.get_object("notebook_structureitems")

		# List table for the connection
		self.db = dbinterface
		
		# Connect the close button
		button = self.builder.get_object("button_refresh")
		button.connect("clicked", self.on_button_refresh_clicked)
		
		button = self.builder.get_object("button_newworksheet")
		button.connect("clicked", self.on_button_newworksheet_clicked)
		
		treeview = self.builder.get_object("treeview_structure")
		treeview.connect("row-activated", self.on_treeview_tables_row_activated, self.builder)

		# Load the database structure
		self.load_database_structure()

		# Add a default worksheet
		self.add_new_worksheet()
			
	def on_treeview_tables_row_activated(self, treeview, path, column, builder):
		model = treeview.get_model()
		iter = model.get_iter(path)
		
		datatype = model.get_value(iter, TYPE_COLUMN)
		
		if datatype == TYPE_ITEM_TABLE or datatype == TYPE_ITEM_SYSTEMTABLE or datatype == TYPE_ITEM_VIEW:
			tablename = model.get_value(iter, LABEL_COLUMN)
			
			# Create the panel and display it
			readonly = (datatype == TYPE_ITEM_SYSTEMTABLE or datatype == TYPE_ITEM_VIEW)
			panel = table.TablePanelView(self.notebook_structureitems, self.db, tablename, readonly)
	
			# The the tab title
			box = gtk.HBox()
			tab_label = gtk.Label(tablename)
			box.pack_start(tab_label, False, False, 0)
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
			box.pack_start(button, False, False, 0)
			box.show_all()
			
			widget, name = panel.get_panel()
			
			# Add the panel
			tabindex = self.notebook_structureitems.append_page(widget, box)
			self.notebook_structureitems.show_all();
			
			# Connect the close button
			button.connect("clicked", self.on_button_tabclose_clicked, panel)
			
	def on_button_tabclose_clicked (self, button, panel):
		widget, name = panel.get_panel()
			
		# Remove the panel
		pagenum = self.notebook_structureitems.page_num(widget)
		self.notebook_structureitems.remove_page(pagenum)

	def on_button_refresh_clicked(self, button):
		self.load_database_structure()

	def on_button_newworksheet_clicked(self, button):
		self.add_new_worksheet()

	def load_database_structure(self):

		# Get database structure info
		dbworker = self.db.get_new_worker()
		dbworker.initialize()
		tables = dbworker.get_tables()
		systemtables = dbworker.get_system_tables()
		views = dbworker.get_views()
		dbworker.dispose()

		model = self.builder.get_object("treestore_structure")
		model.clear()

		# Add tables in the treeview
		root = model.append(None, ["Tables", TYPE_CATEGORY_NAME])
		for item in tables:
			model.append(root, [item, TYPE_ITEM_TABLE])

		# Add system tables in the treeview
		root = model.append(None, ["System tables", TYPE_CATEGORY_NAME])
		for item in systemtables:
			model.append(root, [item, TYPE_ITEM_SYSTEMTABLE])

		# Add views in the treewview
		root = model.append(None, ["Views", TYPE_CATEGORY_NAME])
		for item in views:
			model.append(root, [item, TYPE_ITEM_VIEW])
		
		treeview = self.builder.get_object("treeview_structure")
		treeview.expand_all()

	def add_new_worksheet(self):
		panel = worksheet.WorkSheetPanelView(self.notebook_structureitems, self.db)
		widget, name = panel.get_panel()

		# The the tab title
		box = gtk.HBox()
		tab_label = gtk.Label(name)
		box.pack_start(tab_label, False, False, 0)
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
		box.pack_start(button, False, False, 0)
		box.show_all()
		
		tabindex = self.notebook_structureitems.append_page(widget, box)
		self.notebook_structureitems.show_all();
			
		# Connect the close button
		button.connect("clicked", self.on_button_tabclose_clicked, panel)

		panel.set_focus_text_zone()
		