bl_info = {
    "name": "Versioned Save",
    "author": "Felcon8",
    "version": (1, 4, 0),
    "blender": (3, 0, 0),
    "location": "Preferences > Keymap Customization",
    "description": "Save new versions with a custom recordable hotkey.",
    "category": "System",
    "doc_url": "https://github.com/Felcon8/VersionedSaveAdd-on",
}

import bpy
import os
import re
import datetime
from bpy.props import BoolProperty, EnumProperty

# ------------------------
# Utils
# ------------------------

def get_next_version(filepath, save_type):
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    if save_type == 'TIMESTAMP':
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        base_name = re.sub(r"(_v\d+|_ts\d{4}-\d{2}-\d{2}-\d{2}-\d{2})$", "", name)
        return os.path.join(directory, f"{base_name}_ts{timestamp}{ext}")
    else:
        match = re.search(r"_v(\d+)$", name)
        if match:
            base = name[:match.start()]
            version = int(match.group(1)) + 1
        else:
            base = re.sub(r"_ts\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$", "", name)
            version = 1
        return os.path.join(directory, f"{base}_v{version:03d}{ext}")

# ------------------------
# Preferences
# ------------------------

class VersionedSavePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    enable_versioned_save: BoolProperty(
        name="Use Versioned Save",
        description="Enable/Disable versioning logic",
        default=True
    )

    save_type: EnumProperty(
        name="Type",
        description="Choose how to name your versions",
        items=[
            ('NUMBER', "Number", "Increment version number (e.g. _v001)"),
            ('TIMESTAMP', "Timestamp", "Use current date and time (e.g. _ts2026-01-14)")
        ],
        default='NUMBER'
    )

    def draw(self, context):
        layout = self.layout
        
        # Ссылка на GitHub
        row = layout.row()
        row.operator("wm.url_open", text="GitHub Repository", icon='INFO').url = "https://github.com/Felcon8/VersionedSaveAdd-on"
        
        layout.separator()
        layout.prop(self, "enable_versioned_save")
        
        sub = layout.column()
        sub.enabled = self.enable_versioned_save
        sub.prop(self, "save_type", expand=True)

        # СЕКЦИЯ ГОРЯЧИХ КЛАВИШ (Та самая строчка)
        layout.separator()
        layout.label(text="Click below to record your Hotkey:")
        
        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps.get('Window')
        
        if km:
            # Ищем наш оператор в списке клавиш
            found = False
            for kmi in km.keymap_items:
                if kmi.idname == "wm.ctrl_s_versioned_save":
                    # Отрисовываем строчку записи (нажал -> ввел комбо)
                    col = layout.column(align=True)
                    col.context_pointer_set("keymap",
