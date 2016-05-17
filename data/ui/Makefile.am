## File created by the gnome-build tools

# UI file to install
ui_DATA = \
	main.glade \
	connection_panel.glade \
	table_panel.glade \
	select_connection.glade \
	worksheet_panel.glade \
	queryresult_panel.glade
uidir = $(pkgdatadir)/ui

EXTRA_DIST = \
	$(ui_DATA)

# Remove ui directory on uninstall
uninstall-local:
	-rm -r $(uidir)
