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

PROXY_SUFFIX = ' Proxy'
HI_SUFFIX = ' hi'
LO_SUFFIX = ' lo'


#----------------------------------------------------------------------------------------------------------------------------------------
# Changing Viewport Display for Proxy Objects
#----------------------------------------------------------------------------------------------------------------------------------------

@bpy.app.handlers.persistent
def proxy_pre_render_handler(scene):
    # store source and proxy objects in generators
    source_objects = (obj for obj in bpy.data.objects if obj.name.endswith(HI_SUFFIX))
    proxy_objects = (obj for obj in bpy.data.objects if obj.name.endswith(LO_SUFFIX))

    for obj in scene.objects:
        if obj.type == 'EMPTY' and obj.name.endswith(PROXY_SUFFIX):
            obj.display_type = 'BOUNDS'

    for obj in source_objects:
        obj.hide_viewport = False
        obj.display_type = 'BOUNDS'

    for obj in proxy_objects:
        obj.hide_viewport = True


@bpy.app.handlers.persistent
def proxy_post_render_handler(scene):
    # store source and proxy objects in generators
    source_objects = (obj for obj in bpy.data.objects if obj.name.endswith(HI_SUFFIX))
    proxy_objects = (obj for obj in bpy.data.objects if obj.name.endswith(LO_SUFFIX))

    for obj in source_objects:
        obj.hide_viewport = True
        obj.display_type = 'SOLID'

    for obj in scene.objects:
        if obj.type == 'EMPTY' and obj.name.endswith(PROXY_SUFFIX):
            obj.display_type = 'SOLID'

    for obj in proxy_objects:
        obj.hide_viewport = False


class OBJECT_OT_ProxyPreRender(bpy.types.Operator):
    bl_idname = 'object.proxy_prerender'
    bl_label = 'Pre Render'
    bl_description = 'Set proxy objects display to bounds'

    def execute(self, context):
        proxy_pre_render_handler(context.scene)
        return {'FINISHED'}


class OBJECT_OT_ProxyPostRender(bpy.types.Operator):
    bl_idname = 'object.proxy_postrender'
    bl_label = 'Post Render'
    bl_description = 'Set proxy objects display to vertex cloud'

    def execute(self, context):
        proxy_post_render_handler(context.scene)
        return {'FINISHED'}


class OBJECT_OT_ProxyDisplayOrigin(bpy.types.Operator):
    bl_idname = 'object.proxy_displayorigin'
    bl_label = 'Display Origin'
    bl_description = 'Set proxy objects display to empty'

    def execute(self, context):
        source_objects = (obj for obj in bpy.data.objects if obj.name.endswith(HI_SUFFIX))
        proxy_objects = (obj for obj in bpy.data.objects if obj.name.endswith(LO_SUFFIX))

        for obj in source_objects:
            obj.hide_viewport = True
            obj.display_type = 'SOLID'

        for obj in context.scene.objects:
            if obj.type == 'EMPTY' and obj.name.endswith(PROXY_SUFFIX):
                obj.display_type = 'SOLID'

        for obj in proxy_objects:
            obj.hide_viewport = True
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------------------------
# Vertex Cloud Creation 
# ----------------------------------------------------------------------------------------------------------------------------------------      
class OBJECT_OT_CreateProxy(bpy.types.Operator):
    bl_label = 'Create Proxy'
    bl_idname = 'object.create_proxy'
    bl_description = 'Create vertex cloud proxy object from active object'
    bl_options = {'REGISTER', 'UNDO'}

    # should only work for mesh objects and curves
    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH'

    def execute(self, context):
        scene = context.scene
        proxy_tools = scene.proxy_tools

        # store original location of source object
        original_location = [context.active_object.location[0], context.active_object.location[1],
                            context.active_object.location[2]]

        # reset source object location to world origin
        bpy.ops.object.location_clear(clear_delta=True)

        # store source object data in variable
        source_object = context.active_object
        # create new collection with source object name and proxy object suffix
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True,
                                          new_collection_name=source_object.name + PROXY_SUFFIX)

        # duplicate source object to get proxy object
        bpy.ops.object.duplicate()
        # replace proxy object automatic suffix with lowpoly suffix    
        context.active_object.name = context.active_object.name.replace('.001', LO_SUFFIX)

        # store proxy object data in variable
        proxy_object = context.active_object

        # apply all modifiers
        bpy.ops.object.convert(target='MESH')

        # create vertex cloud representation by deleting all edges and faces and high number of vertices
        bpy.ops.object.mode_set(mode='EDIT')
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='EDGE_FACE')

        # invert mesh
        ratio = max(0.0, 1 - proxy_tools.reduce_verts)
        bpy.ops.mesh.select_random(ratio=ratio)

        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # clear all material slots from proxy object
        # ProxyObject.data.materials.clear()

        # set view modes as required
        proxy_object.hide_render = True
        source_object.hide_viewport = True

        source_object_name = source_object.name
        # add high poly suffix to source object
        source_object.name = source_object.name + HI_SUFFIX

        # if true, collection will be stored in separate .blend file
        if proxy_tools.off_load:
            # set variables 
            filepath = proxy_tools.proxy_path
            data_blocks = set(bpy.data.collections)

            # write proxy collection, source and proxy objects to new blend file
            bpy.data.libraries.write(filepath, data_blocks)

            # link all collections ending with ' Proxy'
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                data_to.collections = [name for name in data_from.collections if name.endswith(PROXY_SUFFIX)]

            # create an empty to instance the linked proxy collection to
            bpy.ops.object.empty_add(type='SINGLE_ARROW')
            # rename ceated empty accordingly
            context.active_object.name = source_object_name + PROXY_SUFFIX
            empty_object = context.active_object

            # remove source and proxy object and original collection
            bpy.data.objects.remove(source_object, do_unlink=True)
            bpy.data.objects.remove(proxy_object, do_unlink=True)
            bpy.data.collections.remove(collection=bpy.data.collections[empty_object.name])

            # instance linked proxy collection to empty
            context.object.instance_collection = bpy.data.collections[empty_object.name]
            # set empty instance type to collection to make proxy collection visible
            context.object.instance_type = 'COLLECTION'

            # place proxy collection at source object location
            context.active_object.location = original_location

        # if false, collection will be unlinked from scene but remain in current .blend file    
        else:
            # create an empty to instance proxy collection
            bpy.ops.object.empty_add(type='SINGLE_ARROW')
            # rename ceated empty accordingly
            context.active_object.name = source_object_name + PROXY_SUFFIX
            empty_object = context.active_object

            context.object.instance_collection = bpy.data.collections[empty_object.name]

            context.object.instance_type = 'COLLECTION'

            # place proxy collection at source object location
            context.active_object.location = original_location

            # unlink collection from scene
            context.scene.collection.children.unlink(context.scene.collection.children[source_object_name + PROXY_SUFFIX])

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

        return {'FINISHED'}