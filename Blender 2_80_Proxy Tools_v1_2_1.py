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


bl_info = {
    "name": "Proxy Tools",
    "author": "xrogueleaderx",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "View3D > UI > Proxy Tools",
    "description": "Tool to create vertex cloud representations of highpoly objects",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

#----------------------------------------------------------------------------------------------------------------------------------------
# Import Modules
#----------------------------------------------------------------------------------------------------------------------------------------
import bpy

from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup,)

from bpy.props import (
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,)

from bpy.app.handlers import (
    persistent,)

def update_display_type(self, context):
    eval('bpy.ops.' + self.display_type_list + '()')
       
#----------------------------------------------------------------------------------------------------------------------------------------
# Define Custom Properties
#----------------------------------------------------------------------------------------------------------------------------------------
class PROPS_UL_ProxyToolProperties(PropertyGroup):    
    #create float property for Reduce Verts
    reduce_verts : FloatProperty(
        name = "Reduce Verts", 
        default =99.80, 
        min = 0.00, 
        max = 99.99, 
        precision = 2, 
        description = "Reduce vertices by percent", 
        subtype = "PERCENTAGE",
        )

    #create string property for Proxy Path
    proxy_path : StringProperty(
        name = "Proxy Path",
        default = "//Proxy.blend",
        description = "Define the directory to store the proxy object file",
        subtype = 'FILE_PATH',
        )

    #create bool property Offload
    off_load : BoolProperty(
        name = "Off Load",  
        description="Store collection data in separate library file",
        default=True,
        )
       
    #create enum property for display type 
    display_type_list : EnumProperty(
        name = "Display Type List",
        items = [("object.proxy_postrender","Point Cloud",'',1),
                ("object.proxy_prerender","Bounds",'',2),
                ("object.proxy_displayorigin","Origin",'',3)],
        description = "Set proxy object display type",
        default="object.proxy_postrender",
        update = update_display_type,
        )
    
#----------------------------------------------------------------------------------------------------------------------------------------
# Changing Viewport Display for Proxy Objects
#----------------------------------------------------------------------------------------------------------------------------------------
@persistent
def ProxyPreRenderHandler(scene):
    #store source and proxy objects in lists
    SourceObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" hi")]
    ProxyObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" lo")]
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY' and obj.name.endswith(" Proxy"):  
            obj.display_type = 'BOUNDS'

    for obj in SourceObjectList:
        obj.hide_viewport = False
        obj.display_type = 'BOUNDS'

    for obj in ProxyObjectList:
        obj.hide_viewport = True
        
@persistent
def ProxyPostRenderHandler(scene):
    #store source and proxy objects in lists
    SourceObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" hi")]
    ProxyObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" lo")] 
         
    for obj in SourceObjectList:
        obj.hide_viewport = True
        obj.display_type = 'SOLID'

    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY' and obj.name.endswith(" Proxy"):  
                obj.display_type = 'SOLID'
                
    for obj in ProxyObjectList:
        obj.hide_viewport = False
        
def ProxyDisplayOrigin(scene):
    #store source and proxy objects in lists
    SourceObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" hi")]
    ProxyObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" lo")] 
         
    for obj in SourceObjectList:
        obj.hide_viewport = True
        obj.display_type = 'SOLID'

    for obj in bpy.context.scene.objects:
        if obj.type == 'EMPTY' and obj.name.endswith(" Proxy"):  
                obj.display_type = 'SOLID'
                
    for obj in ProxyObjectList:
        obj.hide_viewport = True
        
class OBJECT_OT_ProxyPreRender(Operator):
    bl_idname = 'object.proxy_prerender'
    bl_label = 'Pre Render'
    bl_description = 'Set proxy objects display to bounds'
    
    def execute(self, context):
        ProxyPreRenderHandler(bpy.context.scene)
        return {'FINISHED'}

class OBJECT_OT_ProxyPostRender(Operator):
    bl_idname = 'object.proxy_postrender'
    bl_label = 'Post Render'
    bl_description = 'Set proxy objects display to vertex cloud'
    
    def execute(self, context):
        ProxyPostRenderHandler(bpy.context.scene)
        return {'FINISHED'}

class OBJECT_OT_ProxyDisplayOrigin(Operator):
    bl_idname = 'object.proxy_displayorigin'
    bl_label = 'Display Origin'
    bl_description = 'Set proxy objects display to empty'
    
    def execute(self, context):
        ProxyDisplayOrigin(bpy.context.scene)
        return {'FINISHED'}
    
#----------------------------------------------------------------------------------------------------------------------------------------
# Vertex Cloud Creation 
#----------------------------------------------------------------------------------------------------------------------------------------      
class OBJECT_OT_CreateProxy(Operator):
    bl_label = "Create Proxy"
    bl_idname = "object.create_proxy"
    bl_description = "Create vertex cloud proxy object from active object"  
       
    #should only work for mesh objects and curves
    @classmethod
    def poll(cls, context):
        return bpy.context.object.select_get() and bpy.context.object.type == 'MESH'
           
    def execute(self, context):
        scene = context.scene
        proxy_tools = scene.proxy_tools
                
        #store original location of source object
        originalLocation = [bpy.context.active_object.location[0], bpy.context.active_object.location[1],bpy.context.active_object.location[2]]

        #reset source object location to world origin
        bpy.ops.object.location_clear(clear_delta=True)

        #store source object data in variable
        SourceObject = bpy.context.active_object
        #create new collection with source object name and proxy object suffix
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name = SourceObject.name + ' Proxy')

        #duplicate source object to get proxy object
        bpy.ops.object.duplicate()
        #replace proxy object automatic suffix with lowpoly suffix    
        bpy.context.active_object.name = bpy.context.active_object.name.replace('.001',' lo')

        #store proxy object data in variable
        ProxyObject=bpy.context.active_object

        #apply all modifiers
        bpy.ops.object.convert(target='MESH')

        #create vertex cloud representation by deleting all edges and faces and high number of vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='EDGE_FACE')
        bpy.ops.mesh.select_random(percent=proxy_tools.reduce_verts)

        # automatically calculate vertex reduction
        #if len(bpy.context.object.data.vertices) > 5012000:
        #    bpy.ops.mesh.select_random(percent=99.9)
        #elif len(bpy.context.object.data.vertices) > 1024000:
        #    bpy.ops.mesh.select_random(percent=99.8)
        #elif len(bpy.context.object.data.vertices) > 512000:
        #    bpy.ops.mesh.select_random(percent=99.8)
        #elif len(bpy.context.object.data.vertices) > 256000:
        #    bpy.ops.mesh.select_random(percent=99.6)
        #elif len(bpy.context.object.data.vertices) > 128000:
        #    bpy.ops.mesh.select_random(percent=99.2)
        #elif len(bpy.context.object.data.vertices) > 64000:
        #    bpy.ops.mesh.select_random(percent=98.4)
        #elif len(bpy.context.object.data.vertices) > 32000:
        #    bpy.ops.mesh.select_random(percent=96.9)
        #elif len(bpy.context.object.data.vertices) > 16000:
        #    bpy.ops.mesh.select_random(percent=93.5)
        #elif len(bpy.context.object.data.vertices) > 8000:
        #    bpy.ops.mesh.select_random(percent=87.5)
        #elif len(bpy.context.object.data.vertices) > 4000:
        #    bpy.ops.mesh.select_random(percent=75.0)
        #elif len(bpy.context.object.data.vertices) > 2000:
        #    bpy.ops.mesh.select_random(percent=50.0)
        #else:
        #    bpy.ops.mesh.select_random(percent=25.0)

        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        #clear all material slots from proxy object
        #ProxyObject.data.materials.clear()

        #set view modes as required
        ProxyObject.hide_render = True
        SourceObject.hide_viewport = True

        SourceObjectName = SourceObject.name
        #add high poly suffix to source object
        SourceObject.name = SourceObject.name + ' hi'
                
        #if true, collection will be stored in separate .blend file
        if proxy_tools.off_load == True:
            #set variables 
            filepath = proxy_tools.proxy_path
            data_blocks = set(bpy.data.collections)

            #write proxy collection, source and proxy objects to new blend file
            bpy.data.libraries.write(filepath, data_blocks)

            #link all collections ending with ' Proxy'
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                data_to.collections = [name for name in data_from.collections if name.endswith(" Proxy")]
            
            #create an empty to instance the linked proxy collection to
            bpy.ops.object.empty_add(type = 'SINGLE_ARROW')
            #rename ceated empty accordingly
            bpy.context.active_object.name = SourceObjectName + " Proxy"
            EmptyObject = bpy.context.active_object

            #remove source and proxy object and original collection
            bpy.data.objects.remove(SourceObject, do_unlink = True)
            bpy.data.objects.remove(ProxyObject, do_unlink = True)
            bpy.data.collections.remove(collection = bpy.data.collections[EmptyObject.name])

            #instance linked proxy collection to empty
            bpy.context.object.instance_collection = bpy.data.collections[EmptyObject.name]
            #set empty instance type to collection to make proxy collection visible
            bpy.context.object.instance_type = 'COLLECTION'

            #place proxy collection at source object location
            bpy.context.active_object.location = originalLocation
        
        #if false, collection will be unlinked from scene but remain in current .blend file    
        else:                
            #create an empty to instance proxy collection
            bpy.ops.object.empty_add(type = 'SINGLE_ARROW')
            #rename ceated empty accordingly
            bpy.context.active_object.name = SourceObjectName + " Proxy"
            EmptyObject = bpy.context.active_object
            
            bpy.context.object.instance_collection = bpy.data.collections[EmptyObject.name]
            
            bpy.context.object.instance_type = 'COLLECTION'
            
            #place proxy collection at source object location
            bpy.context.active_object.location = originalLocation

            #unlink collection from scene
            bpy.context.scene.collection.children.unlink(bpy.context.scene.collection.children[SourceObjectName + ' Proxy'])
        
        #clean file from unused accumulated datablocks    
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)
                
        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)

        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
        
        return {"FINISHED"}

#### short operator for other script
class OBJECT_OT_CreateProxyTest(Operator):
    bl_label = "Create Proxy Test"
    bl_idname = "object.create_proxy_test"
    bl_description = ""  
       
    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        bpy.ops.object.select_all(action='DESELECT')
        
        if len(sel_objs) > 1:
            for obj in sel_objs:
                bpy.ops.object.create_proxy()
        else:
            bpy.ops.object.create_proxy()   
        return {"FINISHED"}
    
#----------------------------------------------------------------------------------------------------------------------------------------
# UI Panel
#----------------------------------------------------------------------------------------------------------------------------------------  
class OBJECT_PT_ProxyPanel(Panel):
    # create panel in UI under category Proxy
    bl_label = "Create Proxy"
    bl_idname = "TOOLS_PT_CreateProxy"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Proxy Tools"
    bl_context = "objectmode"

    def draw(self, context):
        #store source and proxy objects in lists
        SourceObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" hi")]
        ProxyObjectList = [obj for obj in bpy.data.objects if obj.name.endswith(" lo")]
        
        layout = self.layout
        scene = context.scene
        proxy_tools = scene.proxy_tools

        #create label
        layout.label(text = "Convert Object to Vertex Cloud")
        
        #create slider with Reduce Verts property
        layout.prop(proxy_tools, "reduce_verts", text = "Vertex Reduction")
    
        #create directory selection
        row = layout.row()
        row.prop(proxy_tools, "proxy_path")
    
        #create checkbox for off load geometry
        row = layout.row()
        row.prop(proxy_tools, "off_load", text = "Offload Geometry")
        
        #create conversion button
        row = layout.row()
        row.operator(OBJECT_OT_CreateProxy.bl_idname)
        
        layout.label(text = "Display Type")
        layout.prop(proxy_tools, "display_type_list", text = "")
        
        layout.label(text = "Convert Scene")
        
        row = layout.row()
        #create pre render button
        row.operator(OBJECT_OT_ProxyPreRender.bl_idname, icon = "CUBE")
        #create post render button
        row.operator(OBJECT_OT_ProxyPostRender.bl_idname, icon = "STICKY_UVS_DISABLE")

       
#----------------------------------------------------------------------------------------------------------------------------------------
# Script Registration for Classes and Handlers
#----------------------------------------------------------------------------------------------------------------------------------------
classes = (
    PROPS_UL_ProxyToolProperties,
    OBJECT_PT_ProxyPanel,
    OBJECT_OT_CreateProxy,
    OBJECT_OT_CreateProxyTest,
    OBJECT_OT_ProxyPreRender,
    OBJECT_OT_ProxyPostRender,
    OBJECT_OT_ProxyDisplayOrigin,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
         register_class(cls)
    bpy.app.handlers.render_pre.append(ProxyPreRenderHandler)
    bpy.app.handlers.render_post.append(ProxyPostRenderHandler)
    bpy.types.Scene.proxy_tools = PointerProperty(type = PROPS_UL_ProxyToolProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    bpy.app.handlers.render_pre.remove(ProxyPreRenderHandler)
    bpy.app.handlers.render_post.remove(ProxyPostRenderHandler)
    del bpy.types.Scene.proxy_tools

if __name__ == "__main__":
    register()