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
from app import xdg

class Panel(gobject.GObject):
    """
        The base panel class.

        This class is abstract and should be subclassed.  All subclasses
        should define a 'gladeinfo' and 'name' variables.
    """
    gladeinfo = ('panel.glade', 'PanelWindow')

    def __init__(self, parent, name=None):
		"""
			Intializes the panel
		
			@param controller: the main gui controller
		"""
		gobject.GObject.__init__(self)
		self.name = name
		self.parent = parent

		# if the gladefile starts with file:// use the full path minus
		# file://, otherwise check in the data directories
		gladefile = self.gladeinfo[0]
		if not gladefile.startswith('file://'):
			gladefile = xdg.get_data_path('ui/%s' % gladefile)
		else:
			gladefile = gladefile[7:]
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(gladefile)
		self._child = None

    def get_panel(self):
        if not self._child:
            window = self.builder.get_object(self.gladeinfo[1])
            self._child = window.get_child()
            window.remove(self._child)
            if not self.name:
                self.name = window.get_title()
            window.destroy()

        return (self._child, self.name)

    def __del__(self):
        import appgui
        try:
            #appgui.controller().remove_panel(self._child)
            print "TODO Panel::__del__"
        except ValueError:
            pass
