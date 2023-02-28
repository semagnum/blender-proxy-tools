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

from .proxy_operators import OBJECT_OT_CreateProxy, OBJECT_OT_ProxyPreRender, OBJECT_OT_ProxyPostRender

class OBJECT_PT_ProxyPanel(bpy.types.Panel):
    # create panel in UI under category Proxy
    bl_label = 'Create Proxy'
    bl_idname = 'TOOLS_PT_CreateProxy'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Proxy Tools'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        proxy_tools = scene.proxy_tools

        layout.label(text='Convert Object to Vertex Cloud')
        layout.prop(proxy_tools, 'reduce_verts')

        row = layout.row()
        row.prop(proxy_tools, 'off_load', text='Offload Geometry')
        row = layout.row()
        row.enabled = proxy_tools.off_load
        row.prop(proxy_tools, 'proxy_path', text='')

        row = layout.row()
        row.operator(OBJECT_OT_CreateProxy.bl_idname)

        layout.label(text='Proxy Display Type')
        layout.prop(proxy_tools, 'display_type_list', text='')

        layout.label(text='Convert Scene')

        row = layout.row()
        row.operator(OBJECT_OT_ProxyPreRender.bl_idname, icon='CUBE')
        row.operator(OBJECT_OT_ProxyPostRender.bl_idname, icon='STICKY_UVS_DISABLE')
