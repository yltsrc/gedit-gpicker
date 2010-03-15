from gettext import gettext as _

import os
import gtk
import gconf
import gedit
import subprocess

ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="FileMenu" action="File">
      <placeholder name="FileOps_2">
        <menuitem name="Open Gpicker" action="Gpicker"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class GpickerWindowHelper:
  def __init__(self, plugin, window):
    self._window = window
    self._plugin = plugin
    self._rootdir = os.getcwd()
    self._insert_menu()

  def deactivate(self):
    self._remove_menu()
    self._window = None
    self._plugin = None
    self._action_group = None

  def update_ui(self):
    pass

  def on_gpicker_open(self, action):
    fbroot = self._get_filebrowser_root()
    path = self._rootdir
    if fbroot != "" and fbroot is not None:
      path = fbroot.replace("file://", "")
    if os.path.exists(path):
      cmd = ["gpicker", "-t", "guess", path]
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
      p.wait()
      line = p.stdout.readline()
      if line != "" and line is not None:
        uri = "file://" + os.path.expanduser(path + "/" + line)
        if gedit.utils.uri_is_valid(uri) & gedit.utils.uri_exists(uri):
          self._window.create_tab_from_uri(uri, None, 1, False, True)

  def _insert_menu(self):
    manager = self._window.get_ui_manager()
    self._action_group = gtk.ActionGroup("GpickerPluginActions")
    self._action_group.add_actions([("Gpicker",
                                     None,
                                     _("Open _Gpicker"),
                                     "<control><alt>O",
                                     _("Quick open file with gpicker"),
                                     self.on_gpicker_open)])
    manager.insert_action_group(self._action_group, -1)
    self._ui_id = manager.add_ui_from_string(ui_str)

  def _remove_menu(self):
    manager = self._window.get_ui_manager()
    manager.remove_ui(self._ui_id)
    manager.remove_action_group(self._action_group)
    manager.ensure_update()

  def _get_filebrowser_root(self):
    base = u'/apps/gedit-2/plugins/filebrowser/on_load'
    client = gconf.client_get_default()
    client.add_dir(base, gconf.CLIENT_PRELOAD_NONE)
    path = os.path.join(base, u'virtual_root')
    val = client.get(path)
    if val is not None:
      base = u'/apps/gedit-2/plugins/filebrowser'
      client = gconf.client_get_default()
      client.add_dir(base, gconf.CLIENT_PRELOAD_NONE)
      path = os.path.join(base, u'filter_mode')
      try:
        fbfilter = client.get(path).get_string()
      except AttributeError:
        fbfilter = "hidden"
      if fbfilter.find("hidden") == -1:
        self._show_hidden = True
      else:
        self._show_hidden = False
      return val.get_string()

class GpickerPlugin(gedit.Plugin):
  def __init__(self):
    gedit.Plugin.__init__(self)
    self._instances = {}

  def activate(self, window):
    self._instances[window] = GpickerWindowHelper(self, window)

  def deactivate(self, window):
    self._instances[window].deactivate()
    del self._instances[window]

  def update_ui(self, window):
    self._instances[window].update_ui()

