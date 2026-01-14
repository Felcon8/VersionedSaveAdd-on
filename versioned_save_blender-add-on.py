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
        
        row = layout.row()
        row.operator("wm.url_open", text="GitHub Repository", icon='INFO').url = "https://github.com/Felcon8/VersionedSaveAdd-on"
        
        layout.separator()
        layout.prop(self, "enable_versioned_save")
        
        sub = layout.column()
        sub.enabled = self.enable_versioned_save
        sub.prop(self, "save_type", expand=True)

        layout.separator()
        layout.label(text="Hotkey Configuration:")
        
        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps.get('Window')
        
        if km:
            found = False
            for kmi in km.keymap_items:
                if kmi.idname == "wm.ctrl_s_versioned_save":
                    col = layout.column(align=True)
                    col.context_pointer_set("keymap", km)
                    col.prop(kmi, "type", text="", full_event=True)
                    
                    row = col.row(align=True)
                    row.prop(kmi, "ctrl", text="Ctrl", toggle=True)
                    row.prop(kmi, "shift", text="Shift", toggle=True)
                    row.prop(kmi, "alt", text="Alt", toggle=True)
                    found = True
                    break
            
            if not found:
                layout.label(text="Hotkey entry not found.", icon='ERROR')

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
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
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
