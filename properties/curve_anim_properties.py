import bpy
import logging


logging.getLogger(__name__)


def enable_curve_anim(self, context):
    action = context.object.animation_data.action
    armature = action.curve_anim.armature

    if not context.object.mode == "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')

    if action.curve_anim.turn_it:
        bpy.ops.object.empty_add(
            type='SPHERE',
            align='WORLD',
            location=[0, 0, 0],
            rotation=[0, 0, 0],
            scale=[1, 1, 1],
            )
        left_empty = bpy.data.objects['Empty']
        left_empty.id_data.name = "LeftEmpty"
        left_empty.animation_data_create()
        left_empty.animation_data.action = bpy.data.actions.new(name="LeftHelperAction")
        
        bpy.ops.object.empty_add(
            type='SPHERE',
            align='WORLD',
            location=[0, 0, 0],
            rotation=[0, 0, 0],
            scale=[1, 1, 1],
            )
        right_empty = bpy.data.objects['Empty']
        right_empty.id_data.name = "RightEmpty"
        right_empty.animation_data_create()
        right_empty.animation_data.action = bpy.data.actions.new(name="RightHelperAction")

    else:
        bpy.data.objects['LeftEmpty'].animation_data_clear()
        bpy.data.objects['RightEmpty'].animation_data_clear()
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['LeftEmpty'].select_set(True)
        bpy.data.objects['RightEmpty'].select_set(True)
        bpy.ops.object.delete()

        left_foot = action.curve_anim.foot_bone_left
        right_foot = action.curve_anim.foot_bone_right

        try:
            bpy.data.actions['LeftHelperAction'].user_clear()
            bpy.data.actions['RightHelperAction'].user_clear()
        except KeyError:
            pass

        try:
            c = armature.pose.bones[left_foot].constraints['LeftHelper']
            armature.pose.bones[left_foot].constraints.remove(c)
            c = armature.pose.bones[right_foot].constraints['RightHelper']
            armature.pose.bones[left_foot].constraints.remove(c)
        except KeyError:
            pass

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[armature.name].select_set(True)
    context.view_layer.objects.active = armature
    if not context.object.mode == "POSE":
        bpy.ops.object.mode_set(mode='POSE')


def update_empty_location(self, context):
    action = context.object.animation_data.action
    radius = action.curve_anim.radius
    location_offset = action.curve_anim.location_offset
    bpy.data.objects['LeftEmpty'].location[0] = radius
    bpy.data.objects['RightEmpty'].location[0] = radius
    bpy.data.objects['LeftEmpty'].location[1] = location_offset
    bpy.data.objects['RightEmpty'].location[1] = location_offset

def update_empty_rotation(self, context):
    action = context.object.animation_data.action
    
    for i in range(len(bpy.data.objects['LeftEmpty'].animation_data.action.fcurves[0].keyframe_points[:])):
        og_left = action.curve_anim.og_action['helpers']['action_data'][0][i]
        og_right = action.curve_anim.og_action['helpers']['action_data'][1][i]
        bpy.data.objects['LeftEmpty'].animation_data.action.fcurves[0].keyframe_points[i].co.y = og_left.co.y + action.curve_anim.angle_offset_left
        bpy.data.objects['RightEmpty'].animation_data.action.fcurves[0].keyframe_points[i].co.y = og_right.co.y + action.curve_anim.angle_offset_right



class CurveAnimProperties(bpy.types.PropertyGroup):
    turn_it: bpy.props.BoolProperty(name='Turn it', update=enable_curve_anim)
    radius: bpy.props.FloatProperty(name='Radius', unit="LENGTH", update=update_empty_location)
    back_is_positive: bpy.props.BoolProperty(name='Back is positive')
    location_offset: bpy.props.FloatProperty(name='Location Offset', unit="LENGTH", update=update_empty_location)
    armature: bpy.props.PointerProperty(name='Armature', type=bpy.types.Object)
    foot_bone_left: bpy.props.StringProperty(name='Left Foot Bone')
    foot_bone_right: bpy.props.StringProperty(name='Right Foot Bone')
    left_extremes: dict = {'min': 9999999, 'max': -9999999}
    right_extremes: dict = {'min': 9999999, 'max': -9999999}
    og_action: dict = {'bones': {'bone': [], 'action_data': []}, 'helpers': {'helper': [], 'action_data': []}}
    angle_offset_left: bpy.props.FloatProperty(name='Offset Left', unit="ROTATION", update=update_empty_rotation)
    angle_offset_right: bpy.props.FloatProperty(name='Offset Right', unit="ROTATION", update=update_empty_rotation)

    def clear_og_action(self):
        self.og_action = {'bones': {'bone': [], 'action_data': []}, 'helpers': {'helper': [], 'action_data': []}}
    def reset_min_max(self):
        self.left_extremes = {'min': 9999999, 'max': -9999999}
        self.right_extremes = {'min': 9999999, 'max': -9999999}
