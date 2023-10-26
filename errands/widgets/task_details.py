# Copyright 2023 Vlad Krupinskii <mrvladus@yandex.ru>
# SPDX-License-Identifier: MIT

import os
from errands.utils.markup import Markup
from errands.utils.sync import Sync
from gi.repository import Adw, Gtk, Gio, GLib
from errands.utils.logging import Log
from errands.utils.tasks import task_to_ics


@Gtk.Template(resource_path="/io/github/mrvladus/Errands/task_details.ui")
class TaskDetails(Adw.Window):
    __gtype_name__ = "TaskDetails"

    edit_entry: Adw.EntryRow = Gtk.Template.Child()

    def __init__(self, parent) -> None:
        super().__init__(transient_for=parent.window)
        self.parent = parent
        self._fill_fields()
        self.present()

    def _fill_fields(self):
        self.edit_entry.set_text(self.parent.task["text"])

    @Gtk.Template.Callback()
    def on_copy_text_clicked(self, _btn):
        pass

    @Gtk.Template.Callback()
    def on_move_to_trash_clicked(self, _btn):
        pass

    @Gtk.Template.Callback()
    def on_open_as_ics_clicked(self, _btn):
        cache_dir: str = os.path.join(GLib.get_user_cache_dir(), "tmp")
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        file_path = os.path.join(cache_dir, f"{self.parent.task['id']}.ics")
        with open(file_path, "w") as f:
            f.write(task_to_ics(self.parent.task))
        file: Gio.File = Gio.File.new_for_path(file_path)
        Gtk.FileLauncher.new(file).launch()

    @Gtk.Template.Callback()
    def on_style_selected(self, btn: Gtk.Button) -> None:
        """
        Apply accent color
        """

        for i in btn.get_css_classes():
            color = ""
            if i.startswith("btn-"):
                color = i.split("-")[1]
                break
        # Color card
        for c in self.parent.main_box.get_css_classes():
            if "task-" in c:
                self.parent.main_box.remove_css_class(c)
                break
        self.parent.main_box.add_css_class(f"task-{color}")
        self.parent.task["color"] = color
        self.parent.task["synced_caldav"] = False
        self.parent.update_data()
        Sync.sync()

    @Gtk.Template.Callback()
    def on_text_edited(self, entry: Adw.EntryRow):
        new_text: str = entry.get_text()
        if new_text.strip(" \n\t") == "" or new_text == self.parent.task["text"]:
            entry.set_text(self.parent.task["text"])
            return
        Log.info(f"Edit: {self.parent.task['id']}")
        self.parent.task_row.set_title(Markup.find_url(Markup.escape(new_text)))
        self.parent.task["text"] = new_text
        self.parent.task["synced_caldav"] = False
        self.parent.update_data()
        Sync.sync()