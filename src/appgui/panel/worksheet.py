# worksheet.py
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

import gtk, gobject, glib

from appgui import panel
from appgui.panel import queryresult
import dbconnector
import gtksourceview2
import sqlparse

class WorkSheetPanelView(panel.Panel):

	gladeinfo = ('worksheet_panel.glade', 'window')
	
	def __init__(self, parent, db):
		"""
            Initializes the table panel

            @param parent: the parent dialog
		"""
		panel.Panel.__init__(self, parent, "Worksheet")
		self.db = db

		# Add query result panel
		container = self.builder.get_object("eventbox_queryresult")
		self.queryresult_panel = queryresult.QueryResultPanelView(container)
		widget, name = self.queryresult_panel.get_panel()
		container.add(widget)

		# Configure the GTK source view
		self._sourceview = self.builder.get_object("gtksourceview_worksheet")

		self._lang_manager = gtksourceview2.language_manager_get_default()
		lang = self._lang_manager.get_language('sql')

		srcbuffer = gtksourceview2.Buffer()
		srcbuffer.set_language(lang)

		self._sourceview.set_auto_indent(True)
		self._sourceview.set_buffer(srcbuffer)

		# Connect buttons
		button = self.builder.get_object("button_execute")
		button.connect("clicked", self.on_button_execute_clicked)
		button = self.builder.get_object("button_reformat")
		button.connect("clicked", self.on_button_reformat_clicked)
		button = self.builder.get_object("button_clear")
		button.connect("clicked", self.on_button_clear_clicked)
			
	def on_button_execute_clicked (self, button):

		textbuffer = self._sourceview.get_buffer()

		iterBegin = textbuffer.get_start_iter()
		iterEnd = textbuffer.get_end_iter()
		query = textbuffer.get_text(iterBegin, iterEnd)

		if query != "":
			dbworker = self.db.get_new_worker(self.queryresult_panel)
			dbworker.initialize()

			# Get the query where is located cursor
			markPos = textbuffer.get_insert();
			iterPos = textbuffer.get_iter_at_mark(markPos);
			cur_pos = iterPos.get_offset();
			
			querylist = sqlparse.split(query)
			query = None
			charcount = 0
			for subquery in querylist:
				charcount += len(subquery)
				if charcount >= cur_pos:
					query = subquery
					break

			try:
				query = query.strip()

				# Look if the query is a SELECT
				parsedquery = sqlparse.parse(query)
				is_select = False
				if len(parsedquery)>0 :
					is_select = parsedquery[0].get_type().upper() == "SELECT"
				
				rowcount = dbworker.display_execute_query(query)
				if rowcount == -1 or not is_select:
					self.queryresult_panel.show_console()
				else:
					self.queryresult_panel.show_results()
			except dbconnector.DbConnectorException, e:
				self.queryresult_panel.show_console()

			dbworker.dispose()
			
	def on_button_reformat_clicked (self, button):
		textbuffer = self._sourceview.get_buffer()

		iterBegin = textbuffer.get_start_iter()
		iterEnd = textbuffer.get_end_iter()
		query = textbuffer.get_text(iterBegin, iterEnd)
		query = sqlparse.format(query, reindent=True, keyword_case='upper')

		textbuffer.set_text(query)
			
	def on_button_clear_clicked (self, button):
		textbuffer = self._sourceview.get_buffer()
		textbuffer.set_text("")

	def set_focus_text_zone(self):
		def grab_this(widget):
			widget.grab_focus()
			return False
		glib.idle_add(grab_this, self._sourceview)


		
		