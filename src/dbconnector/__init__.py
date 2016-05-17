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

(
	DBC_FIELD_TYPE_UNKNOW,
	DBC_FIELD_TYPE_INTEGER,
	DBC_FIELD_TYPE_REAL,
	DBC_FIELD_TYPE_TEXT,
	DBC_FIELD_TYPE_BLOB,
) = range(5)

class DbConnector():
	
	"""
        The base DbConnector class.

	    This class is abstract and should be subclassed.
	"""

	def __init__(self, display_name):
		"""
			Intializes the DBConector
		
			@param type: the database type
		"""
		print "init DbConnector"
		self.display_name = display_name

	def __del__(self):
		print "destroy DbConnector"

	# Worker access
	def get_new_worker(self, renderer = None):
		return DbConnectorWorker(self, self.get_dbconnector_interface(), renderer)

	# Override
	def get_dbconnector_interface(self):
		raise NotImplementedError
	
	def get_connection_display_name(self):
		return self.display_name
	
	def get_connection_string(self):
		raise NotImplementedError
		
	def get_use_column_rowid(self):
		return False
		
	def get_column_rowid_name(self):
		raise NotImplementedError

	def get_converted_column_type(self, db_type):

		if db_type != None:
			type_converted = db_type.upper()
		
			if type_converted.find("INTEGER") != -1:
				return DBC_FIELD_TYPE_INTEGER
			if type_converted.find("VARCHAR") != -1:
				return DBC_FIELD_TYPE_TEXT
			if type_converted.find("TEXT") != -1:
				return DBC_FIELD_TYPE_TEXT
			if type_converted.find("SMALLINT") != -1:
				return DBC_FIELD_TYPE_INTEGER
			if type_converted.find("BOOLEAN") != -1:
				return DBC_FIELD_TYPE_INTEGER
			if type_converted.find("DATETIME") != -1:
				return DBC_FIELD_TYPE_TEXT
			
		return DBC_FIELD_TYPE_UNKNOW

class DbConnectorWorker:

	def __init__(self, connector, interface, renderer = None):
		self.connector = connector
		self.interface = interface
		self.conn = None
		self.renderer = renderer

	# Get the connector who create the worker
	def get_connector(self):
		return self.connector

	# General connection method
	def initialize(self):
		self.conn = self.interface.do_initialize(self)
	
	def dispose(self):
		self.interface.do_dispose(self, self.conn)
		self.conn = None
	
	# Table manipulation method
	def get_tables(self):
		return self.interface.do_get_tables(self, self.conn)
	
	def get_system_tables(self):
		return self.interface.do_get_system_tables(self, self.conn)
	
	def get_views(self):
		return self.interface.do_get_views(self, self.conn)
	
	def get_table_description(self, table):
		return self.interface.do_get_table_description(self, self.conn, table)
	
	def display_table_data(self, table, fields, filter):
		return self.interface.do_display_table_data(self, self.conn, table, fields, filter)
	
	def get_table_sql_creation_script(self, table):
		return self.interface.do_get_table_sql_creation_script(self, self.conn, table)

	def display_execute_query(self, query):
		return self.interface.do_display_execute_query(self, self.conn, query)

	# Renderer the data
	def set_view_model(self, rowid_desc, columns, liststore):
		if self.renderer != None:
			return self.renderer.do_set_view_model(self, rowid_desc, columns, liststore)
		return None

	# Log function
	def send_log_query(self, query, rowcount = -1):
		import datetime
		now = datetime.datetime.now()
		if rowcount == None:
			rowcount = -1
		log = "%s => Query executed succesfully: %d row(s) selected/affected\n\t%s\n\n" % (now.strftime("%H:%M:%S"), rowcount, query)
		if self.renderer != None:
			self.renderer.do_write_debug_log(self, log)
	
	def send_log_query_error(self, query, error_text):
		import datetime
		now = datetime.datetime.now()
		log = "%s => Query executed with error(s): %s\n\t%s\n\n" % (now.strftime("%H:%M:%S"), error_text, query)
		if self.renderer != None:
			self.renderer.do_write_debug_log(self, log)
		

class DbConnectorInterface():
	
	# General connection method
	def do_initialize(self, dbworker):
		raise NotImplementedError
	
	def do_dispose(self, dbworker, conn):
		raise NotImplementedError
	
	# Table manipulation method
	def do_get_tables(self, dbworker, conn):
		return []
	
	def do_get_system_tables(self, dbworker, conn):
		return []
	
	def do_get_views(self, dbworker, conn):
		return []
	
	def do_get_table_description(self, dbworker, conn, table):
		raise NotImplementedError
	
	def do_display_table_data(self, dbworker, conn, table, fields, filter):
		raise NotImplementedError
	
	def do_get_table_sql_creation_script(self, dbworker, conn, table):
		raise NotImplementedError

	def do_display_execute_query(self, dbworker, conn, query):
		raise NotImplementedError

class DbActionUiRenderer:
	def do_set_view_model(self, dbworker, rowid_desc, columns, liststore):
		raise NotImplementedError

	def do_write_debug_log(self, dbworker, text):
		print text
		

class DbConnectorException(Exception):
       def __init__(self, connector, value):
           self.parameter = value
       def __str__(self):
           return repr(self.parameter)