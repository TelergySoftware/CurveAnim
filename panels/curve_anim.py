import bpy
import logging


logging.getLogger(__name__)


class CurveAnimPanel(bpy.types.Panel):
    bl_category = "CurveAnim"
    bl_label = "CurveAnim"
    bl_idname = "CA_PT_panel"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        """Make sure there's an active action."""
        active_object = context.object
        if not active_object:
            return False

        animation_data = active_object.animation_data
        if not animation_data:
            return False

        action = animation_data.action
        if not action:
            return False

        return True
    
    def draw(self, context):
        action = context.object.animation_data.action
        layout = self.layout

        row = layout.row()
        row.prop(action.curve_anim, 'turn_it')
        turn_it = action.curve_anim.turn_it

        if not turn_it:
            return

        box = layout.box()
        row = box.row()
        row.prop(action.curve_anim, "radius")

        row = box.row()
        row.prop(action.curve_anim, 'location_offset')

        row = box.row()
        row.prop(action.curve_anim, 'back_is_positive')

        row = box.row()
        row.separator()

        row = box.row()
        row.prop(action.curve_anim, 'armature')
        armature = action.curve_anim.armature
        
        if armature is not None:
            if type(armature.data) == bpy.types.Armature:
                row = box.row()
                row.prop_search(
                    action.curve_anim, "foot_bone_left", armature.data, "bones", text="Left Foot IK"
                )
                row = box.row()
                row.prop_search(
                    action.curve_anim, "foot_bone_right", armature.data, "bones", text="Right Foot IK"
                )
        
        row = box.row()
        row.separator()

        row = box.row()
        row.label(text="Foot turn angle offset:")

        row  = box.row()
        row.prop(action.curve_anim, 'angle_offset_left')

        row  = box.row()
        row.prop(action.curve_anim, 'angle_offset_right')

        row = box.row()
        row.operator("curve_anim.bind")

        row = box.row()
        row.operator("curve_anim.update")
