import bpy
import logging
from math import degrees


logging.getLogger(__name__)


class UpdateAnimation(bpy.types.Operator):
    bl_idname = 'curve_anim.update'
    bl_description = 'Update the action with the new parameters.'
    bl_label = 'Update'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        action = context.object.animation_data.action
        left_empty_action = bpy.data.objects['LeftEmpty'].animation_data.action
        right_empty_action = bpy.data.objects['RightEmpty'].animation_data.action
        lea_exists = left_empty_action is not None
        rea_exists = right_empty_action is not None
        action_exists = action is not None
        is_enabled = action.curve_anim.turn_it
        # left_empty = bpy.data.objects['LeftEmpty']
        # right_empty = bpy.data.objects['RightEmpty']
        return action_exists and lea_exists and rea_exists and is_enabled
    
    def execute(self, context):
        self.action = context.object.animation_data.action

        sce = bpy.context.scene
        current_frame = sce.frame_current

        for f in range(sce.frame_start, sce.frame_end+1):
            sce.frame_set(f)
            self.action.curve_anim.reset_min_max()

            pbone = self.action.curve_anim.armature.pose.bones[self.action.curve_anim.foot_bone_left]
            # print(self.action.curve_anim.og_action[f - sce.frame_start])

            pbone = self.action.curve_anim.armature.pose.bones[self.action.curve_anim.foot_bone_left]
            self.action.curve_anim.left_extremes['max'] = self.action.curve_anim.left_extremes['max'] if self.action.curve_anim.left_extremes['max'] >= pbone.location.y else pbone.location.y # bone in object space
            self.action.curve_anim.left_extremes['min'] = self.action.curve_anim.left_extremes['min'] if self.action.curve_anim.left_extremes['min'] <= pbone.location.y else pbone.location.y

            self.action.curve_anim.right_extremes['max'] = self.action.curve_anim.right_extremes['max'] if self.action.curve_anim.right_extremes['max'] >= pbone.location.y else pbone.location.y # bone in object space
            self.action.curve_anim.right_extremes['min'] = self.action.curve_anim.right_extremes['min'] if self.action.curve_anim.right_extremes['min'] <= pbone.location.y else pbone.location.y

        if self.action.curve_anim.back_is_positive:
            self.action.curve_anim.left_extremes['max'] *= -1
            self.action.curve_anim.left_extremes['min'] *= -1
            
            self.action.curve_anim.right_extremes['max'] *= -1
            self.action.curve_anim.right_extremes['min'] *= -1
        
        print(self.action.curve_anim.right_extremes)

        self.calculate_angle(current_frame)
        
        return {"FINISHED"}
    
    def calculate_angle(self, current_frame):
        sce = bpy.context.scene
        # self.action.curve_anim.og_action = {'bones': {'bone': [], 'action_data': []}, 'helpers': {'helper': [], 'action_data': []}}
        self.action.curve_anim.clear_og_action()
        
        armature = self.action.curve_anim.armature
        left_foot = armature.pose.bones[self.action.curve_anim.foot_bone_left]
        print(self.action.curve_anim.foot_bone_left)
        right_foot = armature.pose.bones[self.action.curve_anim.foot_bone_right]
        left_helper = bpy.data.objects['LeftEmpty']
        right_helper = bpy.data.objects['RightEmpty']

        self.action.curve_anim.og_action['bones']['bone'].append(left_foot)
        self.action.curve_anim.og_action['bones']['bone'].append(right_foot)
        self.action.curve_anim.og_action['helpers']['helper'].append(left_helper)
        self.action.curve_anim.og_action['helpers']['helper'].append(right_foot)

        location_list = left_foot.id_data.animation_data.action.fcurves[1].keyframe_points[:]
        self.action.curve_anim.og_action['bones']['action_data'].append(location_list)
        location_list = right_foot.id_data.animation_data.action.fcurves[1].keyframe_points[:]
        self.action.curve_anim.og_action['bones']['action_data'].append(location_list)

        s_left = self.action.curve_anim.left_extremes['max'] - self.action.curve_anim.left_extremes['min']
        s_right = self.action.curve_anim.right_extremes['max'] - self.action.curve_anim.right_extremes['min']
        theta_left = s_left / self.action.curve_anim.radius
        theta_right = s_right / self.action.curve_anim.radius

        try:
            left_fcu_z = left_helper.animation_data.action.fcurves.new(data_path='rotation_euler', index=2)
            right_fcu_z = right_helper.animation_data.action.fcurves.new(data_path='rotation_euler', index=2)
            
            left_fcu_z.keyframe_points.add(self.action.curve_anim.og_action['bones']['action_data'][0].__len__())
            right_fcu_z.keyframe_points.add(self.action.curve_anim.og_action['bones']['action_data'][1].__len__())
        except RuntimeError:
            left_fcu_z = left_helper.animation_data.action.fcurves[0]
            right_fcu_z = right_helper.animation_data.action.fcurves[0]

        for i, location in enumerate(zip(self.action.curve_anim.og_action['bones']['action_data'][0], self.action.curve_anim.og_action['bones']['action_data'][1])):
            sce.frame_set(location[0].co.x)
            left_empty_z_rot = theta_left * left_foot.location.y / s_left
            sce.frame_set(location[1].co.x)
            right_empty_z_rot = theta_right * right_foot.location.y / s_left

            left_fcu_z.keyframe_points[i].co = location[0].co.x, left_empty_z_rot
            right_fcu_z.keyframe_points[i].co = location[1].co.x, right_empty_z_rot

        
        self.action.curve_anim.og_action['helpers']['action_data'].append(left_fcu_z.keyframe_points[:])
        self.action.curve_anim.og_action['helpers']['action_data'].append(right_fcu_z.keyframe_points[:])

        for i in range(len(self.action.curve_anim.og_action['helpers']['action_data'][0])):
            left_fcu_z.keyframe_points[i].co.y = self.action.curve_anim.og_action['helpers']['action_data'][0][i].co.y + self.action.curve_anim.angle_offset_left
            right_fcu_z.keyframe_points[i].co.y = self.action.curve_anim.og_action['helpers']['action_data'][1][i].co.y + self.action.curve_anim.angle_offset_right

        sce.frame_set(current_frame)