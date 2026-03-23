import bpy
from bpy.props import PointerProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup

class RigResetProperties(PropertyGroup):
    target_rig: PointerProperty(
        name="Target Rig",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE' and (not obj.library or obj.override_library),
        description="Rig to work with"
    )
    apply_confirm: BoolProperty(
        name="Enable Apply as Rest",
        default=False,
        description="Enable the Apply Selected as Rest button"
    )

    show_danger_zone: BoolProperty(
        name="Show Danger Zone",
        default=False
    )

class RigResetPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    enable_danger_section: BoolProperty(
        name="Enable Danger Zone Section (deprecated)",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "enable_danger_section", toggle=False)
        row.label(text="") 

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
    bl_label = "Apply Selected as Rest"
    bl_description = "Apply current pose as rest pose for selected bones"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature in the list")
            return {'CANCELLED'}
        
        if not context.selected_pose_bones:
            self.report({'WARNING'}, "No bones selected!")
            return {'CANCELLED'}

        prev_active = context.view_layer.objects.active
        context.view_layer.objects.active = rig

        bpy.ops.pose.armature_apply()

        context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"Applied selected bones as rest pose")
        return {'FINISHED'}
    
class RIGRESET_OT_toggle_bone_visibility(Operator):
    bl_idname = "rigreset.toggle_bone_visibility"
    bl_label = "Toggle Bone Visibility"
    bl_description = "Show/hide bones in viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        space = context.space_data
        if space and space.type == 'VIEW_3D':
            space.overlay.show_bones = not space.overlay.show_bones
        else:
            self.report({'WARNING'}, "Not a 3D View context")
        return {'FINISHED'}

class RIGRESET_OT_select_rig_and_pose(Operator):
    bl_idname = "rigreset.select_rig_and_pose"
    bl_label = "Select Rig and Pose Mode"
    bl_description = "Select target rig and switch to Pose Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.scene.rigreset_props.target_rig
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "No target rig selected")
            return {'CANCELLED'}

        for obj in context.view_layer.objects:
            obj.select_set(False)
        rig.select_set(True)
        context.view_layer.objects.active = rig
        if rig.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        return {'FINISHED'}
    
class RIGRESET_OT_pose_all_visible(Operator):
    bl_idname = "rigreset.pose_all_visible"
    bl_label = "Pose All Visible Rigs"
    bl_description = "Select all visible armatures and switch to Pose Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        visible_rigs = [obj for obj in context.view_layer.objects 
                        if obj.type == 'ARMATURE' and not obj.hide_get()]
        
        if not visible_rigs:
            self.report({'WARNING'}, "No visible armatures found")
            return {'CANCELLED'}

        if context.active_object:
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        for rig in visible_rigs:
            rig.select_set(True)
        
        context.view_layer.objects.active = visible_rigs[0]
        
        bpy.ops.object.mode_set(mode='POSE')
        
        self.report({'INFO'}, f"Posing {len(visible_rigs)} rig(s)")
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
        rig = props.target_rig
        addon_prefs = context.preferences.addons[__package__].preferences

        row = layout.row(align=True)
        icon = 'HIDE_OFF' if context.space_data.overlay.show_bones else 'HIDE_ON'
        row.operator("rigreset.toggle_bone_visibility", text="", icon=icon)
        row.prop(props, "target_rig", text="")

        col = layout.column(align=True)
        col.operator("rigreset.select_rig_and_pose", text="Select & Pose", icon='OBJECT_DATA')
        col.operator("rigreset.pose_all_visible", text="Pose All Visible", icon='OUTLINER_OB_ARMATURE')

        layout.separator()

        if rig:
            row = layout.row(align=True)
            row.scale_y = 1.2
            row.operator("rigreset.pose_position", text="Pose", icon='ARMATURE_DATA', 
                         depress=(rig.data.pose_position == 'POSE'))
            row.operator("rigreset.rest_position", text="Rest", icon='POSE_HLT', 
                         depress=(rig.data.pose_position == 'REST'))
            
        layout.separator()

        col = layout.column(align=True)
        col.scale_y = 1.3
        col.operator("rigreset.reset_all_to_rest", text="Reset All", icon='LOOP_BACK')
        col.operator("rigreset.reset_selected_to_rest", text="Reset Selected", icon='RESTRICT_SELECT_OFF')

        if rig and addon_prefs.enable_danger_section:

            layout.separator()

            box = layout.box()
            row = box.row(align=True)
            row.prop(props, "show_danger_zone", 
                    icon="TRIA_DOWN" if props.show_danger_zone else "TRIA_RIGHT", 
                    text="", emboss=False)
            row.label(text="DANGER ZONE", icon='ERROR')

            if props.show_danger_zone:
                inner = box.column()
                inner.prop(props, "apply_confirm", text="Enable Modifications")
                
                sub = inner.row()
                sub.enabled = props.apply_confirm
                sub.scale_y = 1.2
                sub.operator("rigreset.apply_as_rest", text="Apply Selected as Rest", icon='CHECKBOX_HLT')

classes = (
    RigResetProperties,
    RigResetPreferences,
    RIGRESET_OT_pose_position,
    RIGRESET_OT_rest_position,
    RIGRESET_OT_reset_all_to_rest,
    RIGRESET_OT_reset_selected_to_rest,
    RIGRESET_OT_apply_as_rest,
    RIGRESET_OT_toggle_bone_visibility,
    RIGRESET_OT_select_rig_and_pose,
    RIGRESET_OT_pose_all_visible,
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