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

import win32com.client
import pywintypes
import os
import time

import dbconnector

class Win32AdoDb(dbconnector.DbConnector, dbconnector.DbConnectorInterface) :

	def __init__(self, display_name, connection_string):
		dbconnector.DbConnector.__init__(self, display_name)
		self.connection_string = connection_string
		
	def get_dbconnector_interface(self):
		return self
		
	def get_connection_string(self):
		return self.connection_string
		
	def get_use_column_rowid(self):
		return False
		
	def get_converted_column_type(self, db_type):

		if db_type != None:
			if db_type == 202 or db_type == 130 or db_type == 203: # TEXT
				return dbconnector.DBC_FIELD_TYPE_TEXT
			if db_type == 17 or db_type == 2 or db_type == 3: # INTEGER
				return dbconnector.DBC_FIELD_TYPE_INTEGER
			if db_type == 11: # BOOLEAN
				return dbconnector.DBC_FIELD_TYPE_INTEGER
			if db_type == 4 or db_type == 5 or db_type == 131: # REAL
				return dbconnector.DBC_FIELD_TYPE_REAL
			if db_type == 7: # DATE
				return dbconnector.DBC_FIELD_TYPE_UNKNOW
			if db_type == 204: # BLOB
				return dbconnector.DBC_FIELD_TYPE_INTEGER
			
		return dbconnector.DBC_FIELD_TYPE_UNKNOW
	
	def do_initialize(self, dbworker):
		#print "Opening :", self.connection_string
		conn = win32com.client.Dispatch(r'ADODB.Connection')
		conn.Open(self.connection_string)
		return conn
		
	def do_dispose(self, dbworker, conn):
		#print "Closing :", self.connection_string
		conn.Close()
		
	def do_get_tables(self, dbworker, conn):
		tables = []
		
		oCat = win32com.client.Dispatch(r'ADOX.Catalog')
		oCat.ActiveConnection = conn
		oTab = oCat.Tables
		for x in oTab:
			if x.Type == 'TABLE':
				tables.append(x.Name)
		
		return tables
		
	def do_get_system_tables(self, dbworker, conn):
		tables = []
		
		oCat = win32com.client.Dispatch(r'ADOX.Catalog')
		oCat.ActiveConnection = conn
		oTab = oCat.Tables
		for x in oTab:
			if x.Type == 'SYSTEM TABLE' or x.Type == 'ACCESS TABLE':
				tables.append(x.Name)
		
		return tables
		
	def do_get_views(self, dbworker, conn):
		views = []
		
		oCat = win32com.client.Dispatch(r'ADOX.Catalog')
		oCat.ActiveConnection = conn
		oTab = oCat.Tables
		for x in oTab:
			if x.Type == 'VIEW':
				views.append(x.Name)
		
		return views
		
	def do_get_table_description(self, dbworker, conn, table):
		columns = []
		
		tables = []
		
		oCat = win32com.client.Dispatch(r'ADOX.Catalog')
		oCat.ActiveConnection = conn
		oTab = oCat.Tables
		for x in oTab:
			if x.Name == table:
				for col in x.Columns:
					columns.append([col.Name, col.Type, False, "", False])
				tables.append(x.Name)
		
		return columns
		
	def do_get_table_sql_creation_script(self, dbworker, conn, table):
		tablesql = ""
		return tablesql
		
	def do_display_table_data(self, dbworker, conn, table, fields, filter):
		rowcount = -1

		rs = win32com.client.Dispatch(r'ADODB.Recordset')
		
		columns_desc = self.do_get_table_description(dbworker, conn, table)
		
		if fields == None:
			fields = list(col[0] for col in columns_desc)
		if len(fields) > 0:
			str_fields = ', '.join(fields)
		else:
			str_fields = '*'
		
		query = "SELECT %s FROM [%s]" % (str_fields, table)
		if filter != None:
			query += " WHERE %s" % filter
		
		try:
			rs.Open(query, conn, 1, 3)
		except pywintypes.com_error, e:
			str = self.get_pywintypes_com_error_string(e)
			dbworker.send_log_query_error(query, str)
			raise dbconnector.DbConnectorException("win32ado", str)
		
		rowcount = self.do_recordset_to_model(dbworker, rs)

		rs.Close()

		dbworker.send_log_query(query, rowcount)
		
		return rowcount

	def do_display_execute_query(self, dbworker, conn, query):
		rowcount = -1

		rs = win32com.client.Dispatch(r'ADODB.Recordset')
		
		try:
			rs.Open(query, conn, 1, 3)
		except pywintypes.com_error, e:
			str = self.get_pywintypes_com_error_string(e)
			dbworker.send_log_query_error(query, str)
			raise dbconnector.DbConnectorException("win32ado", str)
		
		rowcount = self.do_recordset_to_model(dbworker, rs)
			
		rs.Close()

		dbworker.send_log_query(query, rowcount)
		
		return rowcount
		
	def get_pywintypes_com_error_string(self, e):
		return e
		
	def do_recordset_to_model(self, dbworker, rs):
		model_colidx = -1
		model_cols = []
		
		datetimecol = []
		
		columns = []
		for item in rs.Fields:
			# PEP: 249
			# Title: Python Database API Specification v2.0
			# name, type_code, display_size, internal_size, precision, scale, null_ok
			model_colidx = model_colidx+1
			data = {'name':item.Name, 'type_code':item.Type, 'model_colidx':model_colidx}
			model_cols.append(gobject.TYPE_STRING)
			columns.append(data)
			
			if item.Type == 7:
				datetimecol.append(model_colidx)
			
		model = gtk.ListStore(*model_cols)
		dbworker.set_view_model(None, columns, model)
		
		colcount = len(columns)
		
		start = time.clock()
		print "Starting query"
		rowcount = 0
		while not rs.EOF:
			rows=rs.GetRows(1, 0)
			
			rowcount = rowcount + 1
			if rowcount % 500 == 0:
				now = time.clock()
				print "Rowcount = ", rowcount, ", time elapsed = ", (now - start), " ms"

			# Add the row in the model
			row = list(col[0] for col in rows)
			
			# Fixe the display the and date/time outside of epoch (<1970)
			for colidx in datetimecol:
				if row[colidx] != None:
					try:
						str = "%s" % row[colidx]
					except ValueError:
						row[colidx] = repr(row[colidx])
			
			model.append(row)
			
		"""
		start = time.clock()
		print "Starting query"
		rs.MoveFirst()
		rows=rs.GetRows()
		print "GetRows finished"
		rowscount = len(rows[0])
		if rowcount > 0:
			rowcount = 0
			for row in range(rowscount):
				rowcount = rowcount + 1
				
				if rowcount % 250 == 0:
					now = time.clock()
					print "Rowcount = ", rowcount, ", time elapsed = ", (now - start), " ms"
				
				data = []
				for col in range(colcount):
					# Add the row in the model
					data.append(rows[col][row])
			
				model.append(data)
		"""
			
		return rowcount
