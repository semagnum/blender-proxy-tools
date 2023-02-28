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
    "version": (1, 2, 2),
    "blender": (3, 3, 0),
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

from .proxy_tool_props import PROPS_UL_ProxyToolProperties
from .proxy_operators import proxy_pre_render_handler, proxy_post_render_handler
from .proxy_operators import OBJECT_OT_CreateProxy, OBJECT_OT_ProxyPreRender, OBJECT_OT_ProxyPostRender
from .proxy_operators import OBJECT_OT_ProxyDisplayOrigin
from .proxy_panel import OBJECT_PT_ProxyPanel

#----------------------------------------------------------------------------------------------------------------------------------------
# Script Registration for Classes and Handlers
#----------------------------------------------------------------------------------------------------------------------------------------
classes = (
    PROPS_UL_ProxyToolProperties,
    OBJECT_PT_ProxyPanel,
    OBJECT_OT_CreateProxy,
    OBJECT_OT_ProxyPreRender,
    OBJECT_OT_ProxyPostRender,
    OBJECT_OT_ProxyDisplayOrigin,
    )

def register():
    for cls in classes:
         bpy.utils.register_class(cls)
    bpy.app.handlers.render_pre.append(proxy_pre_render_handler)
    bpy.app.handlers.render_post.append(proxy_post_render_handler)
    bpy.types.Scene.proxy_tools = bpy.props.PointerProperty(type = PROPS_UL_ProxyToolProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.render_pre.remove(proxy_pre_render_handler)
    bpy.app.handlers.render_post.remove(proxy_post_render_handler)
    del bpy.types.Scene.proxy_tools

if __name__ == "__main__":
    register()