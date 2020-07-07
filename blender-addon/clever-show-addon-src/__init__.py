import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty
from . operators.export import ExportSwarmAnimation
from . operators.check import CheckSwarmAnimation

bl_info = {
    "name": "clever-show animation (.csv)",
    "author": "Artem Vasiunik & Arthur Golubtsov",
    "version": (0, 6, 1),
    "blender": (2, 83, 0),
    "location": "File > Export > clever-show animation (.csv)",
    "description": "Export > clever-show animation (.csv)",
    "doc_url": "https://github.com/CopterExpress/clever-show/blob/master/blender-addon/README.md",
    "tracker_url": "https://github.com/CopterExpress/clever-show/issues",
    "category": "Import-Export"
}


# noinspection PyArgumentList
class CleverShowProperties(PropertyGroup):
    filter_obj: EnumProperty(
        name="Filter objects:",
        description="",
        items=[('all', "No filter (all objects)", ""),
               ('selected', "Only selected", ""),
               ('name', "By object name", ""),
               ('prop', "By object property", ""),
               ],
        default="selected"
    )

    drones_name: StringProperty(
        name="Name identifier",
        description="Name identifier for all drone objects",
        default="clever"
    )

    speed_limit: FloatProperty(
        name="Speed limit",
        description="Limit of drone movement speed (m/s)",
        unit='VELOCITY',
        default=3,
        min=0,
    )
    distance_limit: FloatProperty(
        name="Distance limit",
        description="Closest possible distance between drones (m)",
        unit='LENGTH',
        default=1.5,
        min=0,
    )


classes = (CleverShowProperties,
           ExportSwarmAnimation, CheckSwarmAnimation)

def menu_func(self, context):
    self.layout.operator(
        ExportSwarmAnimation.bl_idname,
        text="clever-show animation (.csv)"
    )


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.clever_show = PointerProperty(type=CleverShowProperties)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.clever_show

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()