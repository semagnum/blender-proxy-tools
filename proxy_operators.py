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

import bpy


#----------------------------------------------------------------------------------------------------------------------------------------
# Changing Viewport Display for Proxy Objects
#----------------------------------------------------------------------------------------------------------------------------------------

@bpy.app.handlers.persistent
def ProxyPreRenderHandler(scene):
    # store source and proxy objects in lists
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


@bpy.app.handlers.persistent
def ProxyPostRenderHandler(scene):
    # store source and proxy objects in lists
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
    # store source and proxy objects in lists
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


class OBJECT_OT_ProxyPreRender(bpy.types.Operator):
    bl_idname = 'object.proxy_prerender'
    bl_label = 'Pre Render'
    bl_description = 'Set proxy objects display to bounds'

    def execute(self, context):
        ProxyPreRenderHandler(bpy.context.scene)
        return {'FINISHED'}


class OBJECT_OT_ProxyPostRender(bpy.types.Operator):
    bl_idname = 'object.proxy_postrender'
    bl_label = 'Post Render'
    bl_description = 'Set proxy objects display to vertex cloud'

    def execute(self, context):
        ProxyPostRenderHandler(bpy.context.scene)
        return {'FINISHED'}


class OBJECT_OT_ProxyDisplayOrigin(bpy.types.Operator):
    bl_idname = 'object.proxy_displayorigin'
    bl_label = 'Display Origin'
    bl_description = 'Set proxy objects display to empty'

    def execute(self, context):
        ProxyDisplayOrigin(bpy.context.scene)
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------------------------
# Vertex Cloud Creation 
# ----------------------------------------------------------------------------------------------------------------------------------------      
class OBJECT_OT_CreateProxy(bpy.types.Operator):
    bl_label = "Create Proxy"
    bl_idname = "object.create_proxy"
    bl_description = "Create vertex cloud proxy object from active object"

    # should only work for mesh objects and curves
    @classmethod
    def poll(cls, context):
        return bpy.context.object.select_get() and bpy.context.object.type == 'MESH'

    def execute(self, context):
        scene = context.scene
        proxy_tools = scene.proxy_tools

        # store original location of source object
        originalLocation = [bpy.context.active_object.location[0], bpy.context.active_object.location[1],
                            bpy.context.active_object.location[2]]

        # reset source object location to world origin
        bpy.ops.object.location_clear(clear_delta=True)

        # store source object data in variable
        SourceObject = bpy.context.active_object
        # create new collection with source object name and proxy object suffix
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True,
                                          new_collection_name=SourceObject.name + ' Proxy')

        # duplicate source object to get proxy object
        bpy.ops.object.duplicate()
        # replace proxy object automatic suffix with lowpoly suffix    
        bpy.context.active_object.name = bpy.context.active_object.name.replace('.001', ' lo')

        # store proxy object data in variable
        ProxyObject = bpy.context.active_object

        # apply all modifiers
        bpy.ops.object.convert(target='MESH')

        # create vertex cloud representation by deleting all edges and faces and high number of vertices
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='EDGE_FACE')
        bpy.ops.mesh.select_random(ratio=proxy_tools.reduce_verts)

        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # clear all material slots from proxy object
        # ProxyObject.data.materials.clear()

        # set view modes as required
        ProxyObject.hide_render = True
        SourceObject.hide_viewport = True

        SourceObjectName = SourceObject.name
        # add high poly suffix to source object
        SourceObject.name = SourceObject.name + ' hi'

        # if true, collection will be stored in separate .blend file
        if proxy_tools.off_load == True:
            # set variables 
            filepath = proxy_tools.proxy_path
            data_blocks = set(bpy.data.collections)

            # write proxy collection, source and proxy objects to new blend file
            bpy.data.libraries.write(filepath, data_blocks)

            # link all collections ending with ' Proxy'
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                data_to.collections = [name for name in data_from.collections if name.endswith(" Proxy")]

            # create an empty to instance the linked proxy collection to
            bpy.ops.object.empty_add(type='SINGLE_ARROW')
            # rename ceated empty accordingly
            bpy.context.active_object.name = SourceObjectName + " Proxy"
            EmptyObject = bpy.context.active_object

            # remove source and proxy object and original collection
            bpy.data.objects.remove(SourceObject, do_unlink=True)
            bpy.data.objects.remove(ProxyObject, do_unlink=True)
            bpy.data.collections.remove(collection=bpy.data.collections[EmptyObject.name])

            # instance linked proxy collection to empty
            bpy.context.object.instance_collection = bpy.data.collections[EmptyObject.name]
            # set empty instance type to collection to make proxy collection visible
            bpy.context.object.instance_type = 'COLLECTION'

            # place proxy collection at source object location
            bpy.context.active_object.location = originalLocation

        # if false, collection will be unlinked from scene but remain in current .blend file    
        else:
            # create an empty to instance proxy collection
            bpy.ops.object.empty_add(type='SINGLE_ARROW')
            # rename ceated empty accordingly
            bpy.context.active_object.name = SourceObjectName + " Proxy"
            EmptyObject = bpy.context.active_object

            bpy.context.object.instance_collection = bpy.data.collections[EmptyObject.name]

            bpy.context.object.instance_type = 'COLLECTION'

            # place proxy collection at source object location
            bpy.context.active_object.location = originalLocation

            # unlink collection from scene
            bpy.context.scene.collection.children.unlink(
                bpy.context.scene.collection.children[SourceObjectName + ' Proxy'])

        # clean file from unused accumulated datablocks    
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
class OBJECT_OT_CreateProxyTest(bpy.types.Operator):
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
