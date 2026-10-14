import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Gtk, Adw, Gst, GLib

class SlonePlayerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Slone Player - IPTV 📺")
        self.set_default_size(850, 600)

        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_content(main_box)

        # Barra de título nativa Libadwaita
        header = Adw.HeaderBar()
        main_box.append(header)

        # Panel de entrada de enlace IPTV / Stream
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        entry_box.set_margin_start(15)
        entry_box.set_margin_end(15)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Introduce la URL del canal o lista M3U/Stream (http://... / .m3u8)...")
        self.url_entry.set_hexpand(True)
        entry_box.append(self.url_entry)

        btn_play = Gtk.Button(label="▶ Reproducir")
        btn_play.connect("clicked", self.on_play_clicked)
        entry_box.append(btn_play)

        main_box.append(entry_box)

        # Área de estado / reproductor
        self.status_label = Gtk.Label(label="Slone Player listo. Introduce un enlace IPTV para comenzar.")
        self.status_label.set_vexpand(True)
        main_box.append(self.status_label)

        # Inicialización del motor GStreamer
        Gst.init(None)
        self.player = Gst.ElementFactory.make("playbin", "player")

    def on_play_clicked(self, widget):
        url = self.url_entry.get_text().strip()
        if url:
            self.player.set_state(Gst.State.NULL)
            self.player.set_property("uri", url)
            self.player.set_state(Gst.State.PLAYING)
            self.status_label.set_text(f"Cargando/Reproduciendo canal: {url}")

class SloneApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.slone.player")

    def do_activate(self):
        win = SlonePlayerWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = SloneApp()
    app.run(sys.argv)
