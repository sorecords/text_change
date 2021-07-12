# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#  TEXT CHANGE ADD-ON
#  Text Change add-on for Blender 2.83+
#  (c) 2021 Andrey Sokolov (so_records)

bl_info = {
    "name": "Text Change",
    "author": "Andrey Sokolov",
    "version": (1, 0, 0),
    "blender": (2, 83, 3),
    "location": "Object Data Properties > Text",
    "description": "Change text object's text from UI",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Text"
}

import bpy
from bpy.types import Panel, PropertyGroup, TextCurve, Operator, Text
from bpy.props import PointerProperty, StringProperty, EnumProperty
from bpy.utils import register_class, unregister_class

class TextChangeWarning(Operator):
    bl_idname = "txtchng.warning"
    bl_label = "Text Change Warning"
    type : EnumProperty(items={
        ("INFO", "Info", "Info"),
        ("WARNING", "Warning", "Warning"),
        ("ERROR", "Error", "Error")
        },
        default="INFO"
    )
    msg : StringProperty(default="Text Change Warning")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        return {'FINISHED'}
    
    def modal(self, context, event):
        if event:
            self.report({self.type}, self.msg)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class TextChangeUpdate(Operator):
    bl_idname = "txtchng.upd"
    bl_label = "Update Text"
    bl_description = "Update text from source"
    
    @classmethod
    def poll(cls, context):
        return (context.curve is not None and type(context.curve) is TextCurve)
    
    def text_from_text(self) -> str:
        if self.props.text is None:
            msg='Select Blender Text block (can be created in the Text Editor)'
            bpy.ops.txtchng.warning('INVOKE_DEFAULT',type='WARNING', msg=msg)
            return self.curve.body
        text = ""
        for line in self.props.text.lines:
            text+=line.body
            text+='\n'
        return text[:-1]
    
    def text_from_file(self) -> str:
        if self.props.file is None:
            msg='Select Text File. WARNING! Use this at your own risk! Files may contain\
viruses and damage your computer!'
            bpy.ops.txtchng.warning('INVOKE_DEFAULT',type='WARNING', msg=msg)
            return self.curve.body
        fp = bpy.path.abspath(self.props.file)
        with open(fp, 'r') as file:
            text = file.read()
        return text
    
    def execute(self, context):
        self.curve = context.curve
        self.props = self.curve.txtchng
        self.text = ""
        if self.props.source == 'LINE':
            self.text = self.props.line
        elif self.props.source == "TEXT":
            self.text = self.text_from_text()
        elif self.props.source == "FILE":
            self.text = self.text_from_file()
        self.curve.body = self.text
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)
    
def text_change_type_update(self, context):
    if context.curve.txtchng.source == 'FILE':
        msg = 'WARNING! Use this at your own risk! Files may contain \
viruses and may damage your computer!'
        bpy.ops.txtchng.warning('INVOKE_DEFAULT',type='WARNING', msg=msg)
        

def text_change_upd(self, context):
    bpy.ops.txtchng.upd('INVOKE_DEFAULT')
    

class TextChangeProps(PropertyGroup):
    source : EnumProperty(name="Source",
            items={
            ("LINE", "From Line", "Use a single line of text"),
            ("TEXT", "From Text", "Use Text from Blender Text file in \
the Text Editor. Multiple lines can be used"),
            ("FILE", "From File (use with caution!)", "WARNING!\nUse at your own risk!\n\
Files may contain viruses and may damage your computer!\n\
Files in the basic text formats like .txt are preferable")
            },
            default="LINE",
            update=text_change_type_update
    )
    line : StringProperty(name='Text', default='Text', options={'ANIMATABLE'},update=text_change_upd)
    text : PointerProperty(type=Text, name = 'Text', update=text_change_upd)
    file : StringProperty(subtype='FILE_PATH', name = 'File', update=text_change_upd)

class DATA_PT_textchange(Panel):
    bl_label = "Text"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return (context.curve is not None and type(context.curve) is TextCurve)

    def draw(self, context):
        layout = self.layout
        props = context.curve.txtchng
        
        col = layout.column()
        col.prop(props, "source")
        row = col.row()
        if props.source == 'LINE':
            row.prop(props, "line")
        elif props.source == "TEXT":
            row.prop(props, "text")
        elif props.source == "FILE":
            row.prop(props, "file")
        row.operator("txtchng.upd", text="", icon='FILE_REFRESH')
        
classes = [
    TextChangeWarning,
    TextChangeUpdate,
    TextChangeProps,
    DATA_PT_textchange
]

def register():
    for cl in classes:
        register_class(cl)
    bpy.types.TextCurve.txtchng = PointerProperty(type=TextChangeProps)
        
def unregister():
    for cl in reversed(classes):
        unregister_class(cl)
        
#TEST
if __name__ == "__main__":
    register()
