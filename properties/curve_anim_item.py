import bpy


class CurveAnimItem(bpy.types.PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action)