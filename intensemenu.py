bl_info = {
  'name': 'Intense Menu',
  'version': (1, 0, 0),
  'author': 'ComradeIntense',
  'blender': (2, 93, 0),
  'description': 'Simplified access to popular tools. Press D to open the menu',
  'category': 'Interface'
}        

import bpy, bmesh
from bpy.props import BoolProperty

def execute_in_mode(mode, callback):
  previous_mode = 'EDIT' if is_in_editmode() else bpy.context.mode
  bpy.ops.object.mode_set(mode=mode)
  result = callback()
  try: bpy.ops.object.mode_set(mode=previous_mode)
  except: pass
  return result

def is_in_editmode():
  return bpy.context.mode == 'EDIT_MESH'

def anything_is_selected_in_editmode():
  return True in [v.select for v in bmesh.from_edit_mesh(bpy.context.edit_object.data).verts]

def select(obj):
  bpy.ops.object.select_all(action='DESELECT')
  obj.select_set(True)
  bpy.context.view_layer.objects.active = obj
  
# @MainOperator

sk_run = False

class IntenseMenuOperator(bpy.types.Operator):
  """Quick Menu"""
  bl_idname, bl_label = 'in.intensemenu', 'Intense Menu'

  def execute(self, context):
    bpy.ops.wm.call_menu(name=IntenseMenu.bl_idname)
    # Additional actions:
    global sk_run
    if not sk_run:
      sk_run = True
      try:
        if bpy.data.window_managers['WinMan'].enable_screencast_keys:
          bpy.data.window_managers['WinMan'].enable_screencast_keys = False
        bpy.ops.wm.sk_screencast_keys()
        bpy.data.window_managers['WinMan'].enable_screencast_keys = True
      except: pass
    return {'FINISHED'}

class UVSyncOperator(bpy.types.Operator):
  bl_idname, bl_label, bl_options = 'in.uvsync', 'UV Sync', {'REGISTER', 'UNDO'}
  def execute(self, context):
      if context.scene.tool_settings.use_uv_select_sync:
            bpy.context.scene.tool_settings.use_uv_select_sync = False
      else:
            bpy.context.scene.tool_settings.use_uv_select_sync = True

      return {"FINISHED"}
  
class WireframeOperator(bpy.types.Operator):
    bl_idname, bl_label, bl_options = 'in.wireop', '(1) Wireframe', {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.space_data.shading.type = 'WIREFRAME'
        return {"FINISHED"}
class SolidOperator(bpy.types.Operator):
    bl_idname, bl_label, bl_options = 'in.solidop', '(2) Solid', {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.space_data.shading.type = 'SOLID'
        return {"FINISHED"}
class MaterialOperator(bpy.types.Operator):
    bl_idname, bl_label, bl_options = 'in.materialop', '(3) Material', {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.space_data.shading.type = 'MATERIAL'
        return {"FINISHED"}


class JoinSeparateOperator(bpy.types.Operator):
  """Join or Separate"""
  bl_idname, bl_label, bl_options = 'in.join_separate', '(S) Separate / Join', {'REGISTER', 'UNDO'}
  reset_origin: BoolProperty(name='Reset Origin on Separate', default=True)
  
  def execute(self, context):
    if is_in_editmode():
      if anything_is_selected_in_editmode():
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()
        select(bpy.context.selected_objects[-1])
        if self.reset_origin: bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    else:
        bpy.ops.object.join()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
    return {'FINISHED'}

class RotateOperator(bpy.types.Operator):
  """Rotate. Hold shift to invert angle"""
  bl_idname, bl_label, bl_options = 'in.rotate', 'Rotate', {'REGISTER', 'UNDO'}

  def execute(self, context):
    value = 1.5708
    bpy.ops.transform.rotate(value=value, orient_axis='Z', orient_type='GLOBAL')
    return {'FINISHED'}

class SmartUVOperator(bpy.types.Operator):
    bl_idname, bl_label, bl_options = 'in.smartuv', '(3) SmartUV', {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=0, area_weight=0, correct_aspect=True, scale_to_bounds=False)
        return {'FINISHED'}

class ExportSceneOperator(bpy.types.Operator):
    bl_idname = "in.export"
    bl_label = "Export FBX"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}
    
#@IntenseMenu

class IntenseMenu(bpy.types.Menu):

    bl_label = "Intense Menu"
    bl_idname = "OBJECT_MT_intense_menu"
    
    def draw(self, context):
        layout = self.layout
        
        if bpy.context.area.ui_type == 'UV' and context.object.mode == 'EDIT':
            layout.operator('in.rotate', text='(R) Rotate 90')
            layout.operator("object.texel_density_set", text = "(S) Set TD")
            layout.separator()
            FlipUVvert = layout.operator("transform.mirror", text = "Flip Vertical")
            FlipUVvert.orient_matrix_type = 'GLOBAL'
            FlipUVvert.constraint_axis = (False, True, False)
            FlipUVhor = layout.operator("transform.mirror", text = "Flip Horizontal")
            FlipUVhor.orient_matrix_type = 'GLOBAL'
            FlipUVhor.constraint_axis = (True, False, False)
            layout.separator()
            layout.operator("in.uvsync")
            layout.operator("uv.textools_align", text='Align Left').direction='topleft'
            
        else:
            if context.object.mode == 'OBJECT':
                layout.operator("mesh.primitive_cube_add", text = '(A) Add Cube')
                layout.operator("in.join_separate")
                layout.menu(EndMenu.bl_idname)
                
            else:
                layout.operator("mesh.primitive_cube_add", text = '(A) Add Cube')
                layout.operator("in.join_separate")
                
                layout.separator()
                layout.menu(ViewportMenu.bl_idname)   
                layout.menu(FacesMenu.bl_idname)
                layout.menu(MergingMenu.bl_idname)
                layout.menu(deleteclassMenu.bl_idname)
                layout.menu(UnwrapMenu.bl_idname)
                
                layout.separator()                
                flatZ = layout.operator("transform.resize", text = "FlatZ")
                flatZ.value = (1, 1, 0)
                flatZ.orient_type = "GLOBAL"
        
                flatY = layout.operator("transform.resize", text = "FlatY")
                flatY.value = (1, 0, 1)
                flatY.orient_type = "GLOBAL"
                
                flatX = layout.operator("transform.resize", text = "FlatX")
                flatX.value = (0, 0, 1)
                flatX.orient_type = "GLOBAL"
                


class deleteclassMenu(bpy.types.Menu):
    bl_label = '(D) Delete'
    bl_idname = 'in.deldis'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.delete", text = "(1) Delete Face").type='FACE'
        layout.operator("mesh.delete", text = "(2) Delete Vertices").type='VERT'
        layout.operator("mesh.dissolve_edges", text = "(3) Dissolve Edges")
        layout.operator("mesh.dissolve_verts", text = "(4) Dissolve Vertices")

class ViewportMenu(bpy.types.Menu):
    bl_label = '(Q) Switch Viewport'
    bl_idname = 'in.viewportmenu'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("in.wireop")
        layout.operator("in.solidop")
        layout.operator("in.materialop")

class MergingMenu(bpy.types.Menu):
    bl_label = '(E) Merge'
    bl_idname = 'in.mergingmenu'
    def draw(self, context):
        layout = self.layout
        try:
            layout.operator("mesh.merge", text="(1) Last").type= 'LAST'
        except TypeError:
            pass
        layout.operator("mesh.merge", text = "(2) Center").type = 'CENTER'
        layout.operator("mesh.remove_doubles", text = "(3) Distance")
        

class FacesMenu(bpy.types.Menu):
    bl_label = '(W) Faces Menu'
    bl_idname = 'in.facesmenu'
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.flip_normals", text = "(1) Flip Normals")
        layout.operator("mesh.subdivide", text = "(2) Subdivide")
        ngonop = layout.operator("mesh.select_face_by_sides", text = "(3) Show Ngons")
        ngonop.number = 4
        ngonop.type = 'GREATER'        
        layout.operator("mesh.split", text = "(4) Split")

class EndMenu(bpy.types.Menu):
    bl_label = '(E) End Menu'
    bl_idname = 'in.endmenu'
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.origin_set", text='Center Origin').type='ORIGIN_CENTER_OF_MASS'
        layout.operator("view3d.snap_selected_to_cursor", text="Snap 2 cursor").use_offset=False
        layout.operator("object.origin_set", text='Origin 2 cursor').type='ORIGIN_CURSOR'
        apptransform = layout.operator("object.transform_apply", text='All Transform')
        apptransform.location = True
        apptransform.rotation = True
        apptransform.scale = True
        layout.operator("in.export")

class UnwrapMenu(bpy.types.Menu):
    bl_label = '(R) Unwrap'
    bl_idname = 'in.unwrap'
    def draw(self, context):
        layout = self.layout
        UVUnwrap = layout.operator("uv.unwrap", text = "(1) Unwrap")
        UVUnwrap.method = "ANGLE_BASED"
        UVUnwrap.margin = 0.001
        prview = layout.operator("uv.project_from_view", text = "(2) Project from View")
        prview.orthographic=True
        prview.camera_bounds=False
        prview.correct_aspect=True
        prview.scale_to_bounds=False
        layout.operator("in.smartuv")

#class SpinSubmenu(bpy.types.Menu):
#  bl_label, bl_idname = '(C) Spin', 'OBJECT_MT_spin_submenu'

#  def draw(self, context):
#    layout = self.layout
#    layout.operator('in.spin', text='Spin 90').angle = 1.5708
#    layout.operator('in.spin', text='Spin 180').angle = 3.14159265359
#    layout.operator('in.spin', text='Spin 360').angle = 6.28318530718
#    layout.separator()
#    layout.operator('in.spin', text='Spin -90').angle = -1.5708
#    layout.operator('in.spin', text='Spin -180').angle = -3.14159265359


classes = (IntenseMenuOperator, IntenseMenu, MergingMenu, UnwrapMenu, deleteclassMenu, FacesMenu, SmartUVOperator, RotateOperator, JoinSeparateOperator, EndMenu, UVSyncOperator, WireframeOperator, SolidOperator, MaterialOperator, ViewportMenu, ExportSceneOperator)

keymaps = []

def register():
  for c in classes: bpy.utils.register_class(c)
  wm = bpy.context.window_manager
  kc = wm.keyconfigs.addon
  if kc:
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new(IntenseMenuOperator.bl_idname, type='D', value='PRESS')
    keymaps.append((km, kmi))

def unregister():
  for c in classes: bpy.util.unregister_class(c)
  for km, kmi in keymaps:
    km.keymap_items.remove(kmi)
  keymaps.clear()

if __name__ == '__main__': register()