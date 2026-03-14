import bpy
from bpy.props import PointerProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup

class RigResetProperties(PropertyGroup):
    target_rig: PointerProperty(
        name="Target Rig",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE',
        description="Rig to work with"
    )
    apply_confirm: BoolProperty(
        name="Enable Apply as Rest",
        default=False,
        description="Enable the Apply Current as Rest button"
    )

class RIGRESET_OT_pose_position(Operator):
    bl_idname = "rigreset.pose_position"
    bl_label = "Pose Position"
    bl_description = "Show current pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}
        rig.data.pose_position = 'POSE'
        return {'FINISHED'}

class RIGRESET_OT_rest_position(Operator):
    bl_idname = "rigreset.rest_position"
    bl_label = "Rest Position"
    bl_description = "Show rest pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}
        rig.data.pose_position = 'REST'
        return {'FINISHED'}

class RIGRESET_OT_reset_all_to_rest(Operator):
    bl_idname = "rigreset.reset_all_to_rest"
    bl_label = "Reset All to Rest"
    bl_description = "Reset all bones to rest pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}

        prev_active = context.view_layer.objects.active
        prev_mode = rig.mode

        context.view_layer.objects.active = rig
        if rig.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        for pb in rig.pose.bones:
            pb.matrix_basis.identity()

        if prev_mode != 'POSE':
            bpy.ops.object.mode_set(mode=prev_mode)
        context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"Reset all bones of '{rig.name}'")
        return {'FINISHED'}

class RIGRESET_OT_reset_selected_to_rest(Operator):
    bl_idname = "rigreset.reset_selected_to_rest"
    bl_label = "Reset Selected to Rest"
    bl_description = "Reset only selected bones to rest pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}

        prev_active = context.view_layer.objects.active
        prev_mode = rig.mode

        context.view_layer.objects.active = rig
        if rig.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        selected_bones = context.selected_pose_bones
        if not selected_bones:
            if prev_mode != 'POSE':
                bpy.ops.object.mode_set(mode=prev_mode)
            context.view_layer.objects.active = prev_active
            self.report({'INFO'}, "No bones selected")
            return {'CANCELLED'}

        for pb in selected_bones:
            pb.matrix_basis.identity()

        if prev_mode != 'POSE':
            bpy.ops.object.mode_set(mode=prev_mode)
        context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"Reset {len(selected_bones)} bone(s)")
        return {'FINISHED'}

class RIGRESET_OT_apply_as_rest(Operator):
    bl_idname = "rigreset.apply_as_rest"
    bl_label = "Apply Current as Rest"
    bl_description = "Make current pose the new rest pose"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}

        prev_active = context.view_layer.objects.active
        prev_mode = rig.mode

        context.view_layer.objects.active = rig
        if rig.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply()

        if prev_mode != 'POSE':
            bpy.ops.object.mode_set(mode=prev_mode)
        context.view_layer.objects.active = prev_active

        self.report({'WARNING'}, f"New rest pose for '{rig.name}' applied")
        return {'FINISHED'}

class RIGRESET_PT_main_panel(Panel):
    bl_label = "Rig Pose Resetter"
    bl_idname = "RIGRESET_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pose Resetter"

    def draw(self, context):
        layout = self.layout
        props = context.scene.rigreset_props

        layout.prop(props, "target_rig", text="Rig", icon='ARMATURE_DATA')

        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("rigreset.pose_position", text="Pose Position", icon='POSE_HLT')
        col.operator("rigreset.rest_position", text="Rest Position", icon='POSE_HLT')
        col.separator()
        col.operator("rigreset.reset_all_to_rest", text="Reset All to Rest", icon='LOOP_BACK')
        col.operator("rigreset.reset_selected_to_rest", text="Reset Selected to Rest", icon='RESTRICT_SELECT_OFF')

        layout.separator()
        box = layout.box()
        box.label(text="DANGER ZONE", icon='ERROR')
        box.prop(props, "apply_confirm", text="Enable Apply as Rest")
        row = box.row()
        row.enabled = props.apply_confirm
        row.operator("rigreset.apply_as_rest", text="Apply Current as Rest", icon='CHECKBOX_HLT')

classes = (
    RigResetProperties,
    RIGRESET_OT_pose_position,
    RIGRESET_OT_rest_position,
    RIGRESET_OT_reset_all_to_rest,
    RIGRESET_OT_reset_selected_to_rest,
    RIGRESET_OT_apply_as_rest,
    RIGRESET_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rigreset_props = PointerProperty(type=RigResetProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rigreset_props