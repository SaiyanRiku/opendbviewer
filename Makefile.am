## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src \
	data

opendbviewerdocdir = ${prefix}/doc/opendbviewer
opendbviewerdoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


EXTRA_DIST = $(opendbviewerdoc_DATA)


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(opendbviewerdocdir)
