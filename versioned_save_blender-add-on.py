bl_info = {
    "name": "Save New Version on Ctrl+S",
    "author": "ChatGPT",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "Ctrl + S / Preferences",
    "description": "Optionally save new version instead of overwrite on Ctrl+S",
    "category": "System",
}

import bpy
import os
import re
from bpy.props import BoolProperty

# ------------------------
# Utils
# ------------------------

def get_next_version(filepath):
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)

    match = re.search(r"_v(\d+)$", name)
    if match:
        base = name[:match.start()]
        version = int(match.group(1)) + 1
    else:
        base = name
        version = 1

    return os.path.join(directory, f"{base}_v{version:03d}{ext}")

# ------------------------
# Preferences
# ------------------------

class VersionedSavePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    enable_versioned_save: BoolProperty(
        name="Use Versioned Save on Ctrl+S",
        description="Save a new version instead of overwriting when pressing Ctrl+S",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_versioned_save")

# ------------------------
# Operator
# ------------------------

class WM_OT_ctrl_s_versioned_save(bpy.types.Operator):
    bl_idname = "wm.ctrl_s_versioned_save"
    bl_label = "Ctrl+S Versioned Save"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences

        # If выключено — обычный Ctrl+S
        if not prefs.enable_versioned_save:
            bpy.ops.wm.save_mainfile()
            return {'FINISHED'}

        if not bpy.data.filepath:
            self.report({'WARNING'}, "Save file once before versioning")
            return {'CANCELLED'}

        new_path = get_next_version(bpy.data.filepath)
        bpy.ops.wm.save_as_mainfile(filepath=new_path, copy=False)

        self.report({'INFO'}, f"Saved new version: {os.path.basename(new_path)}")
        return {'FINISHED'}

# ------------------------
# Keymap
# ------------------------

addon_keymaps = []

def register():
    bpy.utils.register_class(VersionedSavePreferences)
    bpy.utils.register_class(WM_OT_ctrl_s_versioned_save)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(
        name='Window',
        space_type='EMPTY'
    )

    kmi = km.keymap_items.new(
        WM_OT_ctrl_s_versioned_save.bl_idname,
        type='S',
        value='PRESS',
        ctrl=True
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
