import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, GLib, Gio
import subprocess
import datetime

APP_VERSION = "1.1"
APP_AUTHOR = "Gary Newell"
APP_DESCRIPTION = "EverydayLinuxUserTools monitors Bluetooth and Microsoft fonts."
APP_LICENSE = """GPL v3: This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version."""

# ---------------- Scrolling output dialog ----------------
class CommandOutputDialog(Gtk.Dialog):
    def __init__(self, parent, title, cmd):
        super().__init__(title=title, transient_for=parent, modal=True)
        self.add_buttons("Close", Gtk.ResponseType.CLOSE)
        self.set_default_size(500, 400)

        box = self.get_content_area()
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        box.append(self.scrolled)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        self.scrolled.set_child(self.textview)

        # Start the command
        self.process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        GLib.io_add_watch(self.process.stdout, GLib.IO_IN, self.on_stdout_ready)
        self.connect("response", lambda d, r: self.cleanup())

        self.show()

    def on_stdout_ready(self, source, condition):
        line = source.readline()
        if line:
            self.textbuffer.insert(self.textbuffer.get_end_iter(), line)
            self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0.0, True, 0.0, 1.0)
            return True
        else:
            return False

    def cleanup(self):
        if self.process.poll() is None:
            self.process.terminate()
        self.destroy()

# ---------------- Main Application Window ----------------
class EverydayLinuxUserTools(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="EverydayLinuxUserTools")
        self.set_default_size(600, 400)

        # Header bar with menu
        self.header_bar = Gtk.HeaderBar()
        self.set_titlebar(self.header_bar)
        menu_button = Gtk.MenuButton(label="Menu")
        menu_model = Gio.Menu()
        menu_model.append("About", "app.about")
        menu_button.set_menu_model(menu_model)
        self.header_bar.pack_end(menu_button)

        # Notebook for tabs
        notebook = Gtk.Notebook()
        self.set_child(notebook)

        # Bluetooth tab
        self.bluetooth_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margins(self.bluetooth_tab)
        notebook.append_page(self.bluetooth_tab, Gtk.Label(label="Bluetooth"))
        self.init_bluetooth_tab()

        # Fonts tab
        self.fonts_tab = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margins(self.fonts_tab)
        notebook.append_page(self.fonts_tab, Gtk.Label(label="Fonts"))
        self.init_fonts_tab()

    def set_margins(self, widget, margin=10):
        widget.set_margin_top(margin)
        widget.set_margin_bottom(margin)
        widget.set_margin_start(margin)
        widget.set_margin_end(margin)

    # ---------------- Bluetooth ----------------
    def init_bluetooth_tab(self):
        # Description
        description = ("This shows the current status of your Bluetooth service. "
                       "A green box means Bluetooth is running, a red box means it is stopped. "
                       "Use the button below to start or stop Bluetooth.")
        self.bluetooth_description_label = Gtk.Label(label=description)
        self.bluetooth_description_label.set_wrap(True)
        self.bluetooth_description_label.set_halign(Gtk.Align.START)
        self.bluetooth_tab.append(self.bluetooth_description_label)

        # Status label
        self.bluetooth_status_label = Gtk.Label()
        self.bluetooth_status_label.set_hexpand(True)
        self.bluetooth_status_label.set_halign(Gtk.Align.FILL)
        self.bluetooth_tab.append(self.bluetooth_status_label)

        # Action button
        self.bluetooth_action_button = Gtk.Button()
        self.bluetooth_action_button.set_hexpand(True)
        self.bluetooth_action_button.set_halign(Gtk.Align.FILL)
        self.bluetooth_action_button.connect("clicked", self.toggle_bluetooth)
        self.bluetooth_tab.append(self.bluetooth_action_button)

        self.bluetooth_enabled = self.check_bluetooth_status()
        self.update_bluetooth_ui()

    def check_bluetooth_status(self):
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "bluetooth"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False

    def update_bluetooth_ui(self):
        if self.bluetooth_enabled:
            color = "green"
            text = "Enabled"
            self.bluetooth_action_button.set_label("Disable Bluetooth")
        else:
            color = "red"
            text = "Disabled"
            self.bluetooth_action_button.set_label("Enable Bluetooth")

        # Full width label
        self.bluetooth_status_label.set_markup(
            f'<span background="{color}" foreground="white" size="xx-large"> {text} </span>'
        )

    def toggle_bluetooth(self, button):
        if self.bluetooth_enabled:
            cmd = ["pkexec", "systemctl", "stop", "bluetooth"]
        else:
            cmd = ["pkexec", "systemctl", "start", "bluetooth"]

        dialog = CommandOutputDialog(self, "Bluetooth Operation", cmd)
        dialog.connect("response", lambda d, r: self.refresh_bluetooth_status_once())

    def refresh_bluetooth_status_once(self):
        self.bluetooth_enabled = self.check_bluetooth_status()
        self.update_bluetooth_ui()
        return False

    # ---------------- Fonts ----------------
    def init_fonts_tab(self):
        # Description
        description = ("This shows whether Microsoft fonts (Arial, Verdana, etc.) are installed on your system. "
                       "A green box means they are installed, a red box means they are not. "
                       "Use the button below to install or uninstall these fonts.")
        self.fonts_description_label = Gtk.Label(label=description)
        self.fonts_description_label.set_wrap(True)
        self.fonts_description_label.set_halign(Gtk.Align.START)
        self.fonts_tab.append(self.fonts_description_label)

        # Status label
        self.fonts_status_label = Gtk.Label()
        self.fonts_status_label.set_hexpand(True)
        self.fonts_status_label.set_halign(Gtk.Align.FILL)
        self.fonts_tab.append(self.fonts_status_label)

        # Action button
        self.fonts_action_button = Gtk.Button()
        self.fonts_action_button.set_hexpand(True)
        self.fonts_action_button.set_halign(Gtk.Align.FILL)
        self.fonts_action_button.connect("clicked", self.toggle_fonts)
        self.fonts_tab.append(self.fonts_action_button)

        self.update_fonts_status()

    def update_fonts_status(self):
        fonts_to_check = ["Arial", "Verdana", "Times New Roman", "Tahoma", "Courier New"]
        installed_fonts = []

        try:
            result = subprocess.run(
                ["fc-list", ":family"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            system_fonts = result.stdout.lower()
        except Exception:
            system_fonts = ""

        for font in fonts_to_check:
            if font.lower() in system_fonts:
                installed_fonts.append(font)

        if installed_fonts:
            color = "green"
            text = "Microsoft fonts installed"
            self.fonts_action_button.set_label("Uninstall")
        else:
            color = "red"
            text = "Microsoft fonts not installed"
            self.fonts_action_button.set_label("Install")

        # Full width label
        self.fonts_status_label.set_markup(
            f'<span background="{color}" foreground="white" size="xx-large"> {text} </span>'
        )

        self.installed_fonts = installed_fonts

    def toggle_fonts(self, button):
        if self.installed_fonts:
            cmd = ["pkexec", "yay", "-R", "--noconfirm", "ttf-ms-fonts"]
        else:
            cmd = ["pkexec", "yay", "-S", "--noconfirm", "ttf-ms-fonts"]

        dialog = CommandOutputDialog(self, "Fonts Operation", cmd)
        dialog.connect("response", lambda d, r: self.update_fonts_status())

    # ---------------- About ----------------
    def show_about(self, action, param=None):
        today = datetime.date.today().isoformat()
        text = f"{APP_DESCRIPTION}\nVersion: {APP_VERSION}\nAuthor: {APP_AUTHOR}\nDate: {today}\n\n{APP_LICENSE}"
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, text=text, buttons=Gtk.ButtonsType.OK
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

# ---------------- Application ----------------
class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.everydaylinuxusertools.app")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect(
            "activate",
            lambda a, p: self.get_active_window().show_about(None)
        )
        self.add_action(about_action)

        win = EverydayLinuxUserTools(self)
        win.present()

if __name__ == "__main__":
    app = App()
    app.run()