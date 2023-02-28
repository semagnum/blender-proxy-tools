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


def update_display_type(self, context):
    eval('bpy.ops.' + self.display_type_list + '()')

class PROPS_UL_ProxyToolProperties(bpy.types.PropertyGroup):
    # create float property for Reduce Verts
    reduce_verts: bpy.props.FloatProperty(
        name="Reduce Verts",
        default=0.998,
        min=0.00,
        max=0.99,
        precision=2,
        description="Reduce vertices by percent",
        subtype="PERCENTAGE",
    )

    # create string property for Proxy Path
    proxy_path: bpy.props.StringProperty(
        name="Proxy Path",
        default="//Proxy.blend",
        description="Define the directory to store the proxy object file",
        subtype='FILE_PATH',
    )

    # create bool property Offload
    off_load: bpy.props.BoolProperty(
        name="Off Load",
        description="Store collection data in separate library file",
        default=True,
    )

    # create enum property for display type
    display_type_list: bpy.props.EnumProperty(
        name="Display Type List",
        items=[("object.proxy_postrender", "Point Cloud", '', 1),
               ("object.proxy_prerender", "Bounds", '', 2),
               ("object.proxy_displayorigin", "Origin", '', 3)],
        description="Set proxy object display type",
        default="object.proxy_postrender",
        update=update_display_type,
    )
