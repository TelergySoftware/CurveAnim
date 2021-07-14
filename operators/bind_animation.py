import bpy
import logging


logging.getLogger(__name__)


class BindUnbindAnimation(bpy.types.Operator):
    bl_idname = 'curve_anim.bind'
    bl_description = 'Bind or Unbind the action to the helper empties.'
    bl_label = 'Bind/Unbind'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        action = context.object.animation_data.action
        action_exists = action is not None
        is_enabled = action.curve_anim.turn_it
        # left_empty = bpy.data.objects['LeftEmpty']
        # right_empty = bpy.data.objects['RightEmpty']
        return action_exists and is_enabled
    
    def execute(self, context):
        self.action = context.object.animation_data.action

        self.bind_unbind()

        return {"FINISHED"}
    
    def bind_unbind(self):
        armature = self.action.curve_anim.armature
        left_foot = self.action.curve_anim.foot_bone_left
        right_foot = self.action.curve_anim.foot_bone_right

        left_empty = bpy.data.objects['LeftEmpty']
        right_empty = bpy.data.objects['RightEmpty']

        try:
            c = armature.pose.bones[left_foot].constraints['LeftHelper']
            armature.pose.bones[left_foot].constraints.remove(c)
            c = armature.pose.bones[right_foot].constraints['RightHelper']
            armature.pose.bones[left_foot].constraints.remove(c)
        except KeyError:
            left_constraint = armature.pose.bones[left_foot].constraints.new(type='CHILD_OF')
            left_constraint.target = left_empty
            left_constraint.name = "LeftHelper"
            right_constraint = armature.pose.bones[right_foot].constraints.new(type='CHILD_OF')
            right_constraint.target = right_empty
            right_constraint.name = "RightHelper"
