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

from __future__ import absolute_import # Allow to declare and use an sqlite3 module

import gtk, gobject

import sqlite3

import dbconnector

class SQLite3(dbconnector.DbConnector, dbconnector.DbConnectorInterface):

	def __init__(self, display_name, connection_string):
		dbconnector.DbConnector.__init__(self, display_name)
		self.connection_string = connection_string
		
	def get_dbconnector_interface(self):
		return self
		
	def get_connection_string(self):
		return self.connection_string
		
	def get_use_column_rowid(self):
		return True
		
	def get_column_rowid_name(self):
		return "rowid"
	
	def do_initialize(self, dbworker):
		#print "Opening :", self.connection_string
		conn = sqlite3.connect(self.connection_string)
		conn.row_factory = sqlite3.Row
		return conn
		
	def do_dispose(self, dbworker, conn):
		#print "Closing :", self.connection_string
		conn.close()
		
	def do_get_tables(self, dbworker, conn):
		tables = []
		
		c = conn.cursor()
		
		query = "SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'sqlite_sequence' ORDER BY name;"
		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		rowcount = 0
		for line in c:
			tables.append(line["name"])
			rowcount = rowcount + 1
			
		dbworker.send_log_query(query, rowcount)
				
		c.close()
		
		return tables
		
	def do_get_system_tables(self, dbworker, conn):
		tables = ['sqlite_master', 'sqlite_sequence']
		
		return tables

	def do_get_views(self, dbworker, conn):
		views = []
		
		c = conn.cursor()
		
		query = "SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name;"
		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		rowcount = 0
		for line in c:
			views.append(line["name"])
			rowcount = rowcount + 1
			
		dbworker.send_log_query(query, rowcount)
				
		c.close()
		
		return views
		
	def do_get_table_description(self, dbworker, conn, table):
		columns = []
	
		c = conn.cursor()
		query = "PRAGMA table_info(%s);" % (table)

		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		rowcount = 0
		for line in c:
			# cid, name, type, notnull, dfltvalue, pk
			columns.append([line["name"], line["type"], line["notnull"], line[4], line["pk"]])
			rowcount = rowcount + 1
			
		dbworker.send_log_query(query, rowcount)
				
		c.close()
		
		return columns
		
	def do_get_table_sql_creation_script(self, dbworker, conn, table):
		tablesql = ""
	
		c = conn.cursor()
		query = "SELECT sql FROM sqlite_master WHERE type = 'table' AND name='%s';" % (table)

		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		rowcount = 0
		for line in c:
			tablesql = line["sql"]
			rowcount = rowcount + 1

		dbworker.send_log_query(query, rowcount)
				
		c.close()
		
		return tablesql
		
	def do_display_table_data(self, dbworker, conn, table, fields, filter):
		use_rowid = self.get_use_column_rowid()
		rowid_name = self.get_column_rowid_name()
		rowcount = -1

		columns_desc = self.do_get_table_description(dbworker, conn, table)
	
		c = conn.cursor()

		if fields == None:
			fields = list(col[0] for col in columns_desc)
		if len(fields) > 0:
			str_fields = ', '.join(fields)
		else:
			str_fields = '*'
		
		query = "SELECT rowid as rowid, %s FROM %s" % (str_fields, table)
		if filter != None:
			query += " WHERE %s" % filter

		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		model_colidx = -1
		model_cols = []

		# Add the rowid column in the model
		model_colidx = model_colidx+1
		rowid_colidx = model_colidx
		model_cols.append(gobject.TYPE_STRING)
			
		if c.description != None:
			# Get the colums and set the model to store the data
			columns = []
			
			for col in c.description:
				if col[0] != rowid_name:
					# PEP: 249
					# Title: Python Database API Specification v2.0
					# name, type_code, display_size, internal_size, precision, scale, null_ok
					type_code = None
					for desc in columns_desc: 
						if desc[0] == col[0]:
							type_code = desc[1]
					model_colidx = model_colidx+1
					data = {'name':col[0], 'type_code':type_code, 'model_colidx':model_colidx}
					model_cols.append(gobject.TYPE_STRING)
					columns.append(data)
			
			rowid_desc = {'use_rowid':use_rowid, 'rowid_name':rowid_name, 'rowid_colidx':rowid_colidx}

			model = gtk.ListStore(*model_cols)
			dbworker.set_view_model(rowid_desc, columns, model)

			# If we have a model, we put the data in
			if model != None:
				rowcount = 0
				row = c.fetchone()
				while row != None:
					rowcount = rowcount + 1
				
					# Add the row in the model
					data = []
					data.extend(row)
					model.append(data)

					# Next row
					row = c.fetchone()

		dbworker.send_log_query(query, rowcount)
		
		c.close()
		
		return rowcount

	def do_display_execute_query(self, dbworker, conn, query):

		rowcount = -1
		
		c = conn.cursor()

		try:
			c.execute(query)
		except sqlite3.Error, e:
			c.close()
			dbworker.send_log_query_error(query, e.args[0])
			raise dbconnector.DbConnectorException("sqlite3", e.args[0])

		model_colidx = -1
		model_cols = []
		
		if c.description != None:
			columns = []
			for col in c.description:
				# PEP: 249
				# Title: Python Database API Specification v2.0
				# name, type_code, display_size, internal_size, precision, scale, null_ok
				model_colidx = model_colidx+1
				data = {'name':col[0], 'type_code':col[1], 'model_colidx':model_colidx}
				model_cols.append(gobject.TYPE_STRING)
				columns.append(data)
			
			model = gtk.ListStore(*model_cols)
			dbworker.set_view_model(None, columns, model)

			# If we have a model, we put the data in
			if model != None:
				rowcount = 0
				row = c.fetchone()
				while row != None:
					rowcount = rowcount + 1
				
					# Add the row in the model
					data = []
					data.extend(row)
					model.append(data)

					# Next row
					row = c.fetchone()

		dbworker.send_log_query(query, rowcount)

		if rowcount == -1:
			conn.commit();

		c.close()
		
		return rowcount
		
		
