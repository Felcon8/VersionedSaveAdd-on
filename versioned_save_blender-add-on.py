bl_info = {
    "name": "Versioned Save",
    "author": "Felcon8",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "Ctrl + S / Preferences",
    "description": "Save new versions (Number or Timestamp) instead of overwrite on Ctrl+S",
    "category": "System",
    "doc_url": "https://github.com/Felcon8/VersionedSaveAdd-on", # Ваша ссылка здесь
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
        # Format: YYYY-MM-DD-HH-MM
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        # Clean old version or timestamp suffixes
        base_name = re.sub(r"(_v\d+|_ts\d{4}-\d{2}-\d{2}-\d{2}-\d{2})$", "", name)
        return os.path.join(directory, f"{base_name}_ts{timestamp}{ext}")

    else:  # NUMBER mode
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
        name="Use Versioned Save on Ctrl+S",
        description="Enable/Disable versioning logic",
        default=True
    )

    save_type: EnumProperty(
        name="Type",
        description="Choose how to name your versions",
        items=[
            ('NUMBER', "Number", "Increment version number (e.g. _v001)"),
            ('TIMESTAMP', "Timestamp", "Use current date and time (e.g. _ts2026-01-14-14-30)")
        ],
        default='NUMBER'
    )

    def draw(self, context):
        layout = self.layout
        
        # Ссылка на GitHub прямо в настройках
        row = layout.row()
        row.operator("wm.url_open", text="GitHub Repository", icon='INFO').url = "https://github.com/Felcon8/VersionedSaveAdd-on"
        
        layout.separator()
        layout.prop(self, "enable_versioned_save")
        
        sub = layout.column()
        sub.enabled = self.enable_versioned_save
        sub.prop(self, "save_type", expand=True)

# ------------------------
# Operator
# ------------------------

class WM_OT_ctrl_s_versioned_save(bpy.types.Operator):
    bl_idname = "wm.ctrl_s_versioned_save"
    bl_label = "Versioned Save"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        if not prefs.enable_versioned_save:
            bpy.ops.wm.save_mainfile()
            return {'FINISHED'}

        if not bpy.data.filepath:
            self.report({'WARNING'}, "Save file once before versioning")
            return {'CANCELLED'}

        new_path = get_next_version(bpy.data.filepath, prefs.save_type)
        bpy.ops.wm.save_as_mainfile(filepath=new_path, copy=False)

        self.report({'INFO'}, f"Saved: {os.path.basename(new_path)}")
        return {'FINISHED'}

# ------------------------
# Registration
# ------------------------

addon_keymaps = []

def register():
    bpy.utils.register_class(VersionedSavePreferences)
    bpy.utils.register_class(WM_OT_ctrl_s_versioned_save)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new(
        WM_OT_ctrl_s_versioned_save.bl_idname,
        type='S', value='PRESS', ctrl=True
    )
    addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(WM_OT_ctrl_s_versioned_save)
    bpy.utils.unregister_class(VersionedSavePreferences)

if __name__ == "__main__":
    register()
