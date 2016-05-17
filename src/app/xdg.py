# Copyright (C) Eric Beuque 2011 <eric.beuque@gmail.com>
# Imported from Exaile project
# Copyright (C) 2008-2009 Adam Olsen
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

import os

homedir = os.path.expanduser("~")
lastdir = homedir

data_home = os.getenv("XDG_DATA_HOME")
if data_home == None:
    data_home = os.path.join(homedir, ".local", "share")
data_home = os.path.join(data_home, "opendbviewer")
if not os.path.exists(data_home):
    os.makedirs(data_home)

config_home = os.getenv("XDG_CONFIG_HOME")
if config_home == None:
    config_home = os.path.join(homedir, ".config")
config_home = os.path.join(config_home, "opendbviewer")
if not os.path.exists(config_home):
    os.makedirs(config_home)

cache_home = os.getenv("XDG_CACHE_HOME")
if cache_home == None:
    cache_home = os.path.join(homedir, ".cache")
cache_home = os.path.join(cache_home, "opendbviewer")
if not os.path.exists(cache_home):
    os.makedirs(cache_home)

data_dirs = os.getenv("XDG_DATA_DIRS")
if data_dirs == None:
    data_dirs = "/usr/local/share/:/usr/share/:/opt/share/"
data_dirs = [os.path.join(d, "opendbviewer") for d in data_dirs.split(":")]

config_dirs = os.getenv("XDG_CONFIG_DIRS")
if config_dirs == None:
    config_dirs = "/etc/xdg"
config_dirs = [os.path.join(d, "opendbviewer") for d in config_dirs.split(":")]

app_dir = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
# Detect if application is not installed.
if os.path.exists(os.path.join(app_dir, 'Makefile')):
    # Insert the "data" directory to data_dirs.
    data_dir = os.path.join(app_dir, 'data')
    data_dirs.insert(0, data_dir)
    # insert the config dir
    config_dir = os.path.join(app_dir, 'data', 'config')
    config_dirs.insert(0, config_dir)
    # Create a symlink from plugins to data/plugins.
    plugins_dir = os.path.join(data_dir, 'plugins')
    if not os.path.exists(plugins_dir):
        try:
            os.symlink(os.path.join(app_dir, 'plugins'), plugins_dir)
        except (AttributeError, OSError):
            # If the system does not support symlinks, ignore.
            pass

data_dirs.insert(0, data_home)

def get_config_dir():
    return config_home

def get_config_dirs():
    return config_dirs

def get_data_dirs():
    return data_dirs[:]

def get_cache_dir():
    return cache_home

def get_data_path(*subpath_elements):
    subpath = os.path.join(*subpath_elements)
    for dir in data_dirs:
        path = os.path.join(dir, subpath)
        if os.path.exists(path):
            return path
    return None

def get_config_path(*subpath_elements):
    subpath = os.path.join(*subpath_elements)
    for dir in config_dirs:
        path = os.path.join(dir, subpath)
        if os.path.exists(path):
            return path
    return None

def get_last_dir():
    return lastdir

def get_plugin_data_dir():
    path = os.path.join(get_data_dirs()[0], 'plugin_data')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# vim: et sts=4 sw=4

