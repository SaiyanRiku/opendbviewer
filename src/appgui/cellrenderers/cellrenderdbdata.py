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


import gtk, gobject
import pango

DATATYPE_UNKNOW  = 0
DATATYPE_INTEGER = 1
DATATYPE_REAL    = 2
DATATYPE_TEXT    = 3
DATATYPE_BLOB    = 4

MAX_LEN_DATATYPE_TEXT = 100

class CellRendererDBData(gtk.CellRendererText):

	__gsignals__ = {
	}

	__gproperties__ = {
		'data-text' : (gobject.TYPE_STRING, "Cell text",
			"The text to display", None, gobject.PARAM_READWRITE),
		'data-type': (gobject.TYPE_LONG, "Data type",
			"The type of data in the cell", 0, 10, 0, gobject.PARAM_READWRITE),
	}
	
	def __init__(self):
		gtk.CellRendererText.__init__(self)
		self.data_text = None
		self.data_type = DATATYPE_UNKNOW

	def do_render(self, window, widget, backround_area, cell_area, expose_area, flags):
		self.update_cell_renderer()

		if self.data_type == DATATYPE_INTEGER or self.data_type == DATATYPE_REAL: 
			self.set_property("alignment", pango.ALIGN_RIGHT)
			self.set_property("xalign", 1)
		
		return gtk.CellRendererText.do_render(self, window, widget, backround_area, cell_area, expose_area, flags)

	def do_get_size(self, widget, cell_area):
		self.update_cell_renderer()
		size = gtk.CellRendererText.do_get_size(self, widget, cell_area)
		return size

	def do_get_property(self, param_spec):
		name = param_spec.name.replace("-", "_")
		return getattr(self, name)

	def do_set_property(self, param_spec, value):
		name = param_spec.name.replace("-", "_")	
		setattr(self, name, value)

	def update_cell_renderer(self):
		text = self.data_text
		state = gtk.STATE_NORMAL
		if text == None:
			text = "NULL"
			self.set_property("style", pango.STYLE_ITALIC)
			state = gtk.STATE_INSENSITIVE
		elif self.data_type == DATATYPE_BLOB:
			text = "(blob)"
			self.set_property("style", pango.STYLE_ITALIC)
		else:
			if self.data_type == DATATYPE_TEXT:
				# Format the text only one line
				import re
				text = re.sub("\s+" , " ", text)
				text = text.replace('\n', "")
				text = text.replace('\t', "")
				if len(text) >= MAX_LEN_DATATYPE_TEXT:
					text = "%s..." % text[:MAX_LEN_DATATYPE_TEXT]
			self.set_property("style", pango.STYLE_NORMAL)
		self.set_property("text", text)

	def set_data_type(self, data_type):
		self.data_type = data_type

gobject.type_register(CellRendererDBData)