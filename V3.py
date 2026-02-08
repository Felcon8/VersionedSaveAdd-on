bl_info = {
    "name": "Versioned Save",
    "author": "Felcon8",
    "version": (1, 4, 3),
    "blender": (3, 0, 0),
    "location": "Preferences > Keymap Customization",
    "description": "Advanced Versioning with forced Recent Files update.",
    "category": "System",
}

import bpy
import os
import re
import datetime
from bpy.props import BoolProperty, EnumProperty

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

class VersionedSavePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    enable_versioned_save: BoolProperty(name="Use Versioned Save", default=True)
    save_type: EnumProperty(
        name="Mode",
        items=[('NUMBER', "Number", ""), ('TIMESTAMP', "Timestamp", "")],
        default='NUMBER'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_versioned_save")
        layout.prop(self, "save_type", expand=True)
        
        wm = context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps.get('Window')
        if km:
            for kmi in km.keymap_items:
                if kmi.idname == "wm.ctrl_s_versioned_save":
                    layout.label(text="Hotkey:")
                    layout.prop(kmi, "type", text="", full_event=True)
                    break

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
            
        old_path = bpy.data.filepath
        new_path = get_next_version(old_path, prefs.save_type)
        
        # Сохраняем текущий файл под новым именем
        bpy.ops.wm.save_as_mainfile(filepath=new_path, check_existing=False, copy=False)
        
        # Принудительно прописываем путь в данные Блендера, если он не обновился
        bpy.data.filepath = new_path 
        
        # Обновляем Recent Files через встроенную команду
        bpy.ops.wm.append_recent_files()
        
        # Финальный штрих: сохраняем настройки, это триггерит обновление конфига последних файлов
        bpy.ops.wm.save_userpref()
            
        self.report({'INFO'}, f"Version Saved: {os.path.basename(new_path)}")
        return {'FINISHED'}

addon_keymaps = []

def register():
    bpy.utils.register_class(VersionedSavePreferences)
    bpy.utils.register_class(WM_OT_ctrl_s_versioned_save)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new(WM_OT_ctrl_s_versioned_save.bl_idname, type='S', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_class(WM_OT_ctrl_s_versioned_save)
    bpy.utils.unregister_class(VersionedSavePreferences)

if __name__ == "__main__":
    register()
