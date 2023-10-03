bl_info = {
    "name": "Blockland brick (.blb) format",
    "author": "siba",
    "blender": (2, 79, 0),
    "location": "File > Import",
    "description": "Import Blockland bricks",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'OFFICIAL',
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if "import_blb" in locals():
        imp.reload(import_blb)
else:
    import bpy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class Import_blb_class(Operator, ImportHelper):
    """Load a Blockland brick (.blb) file"""
    bl_idname = "import_mesh.blb"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import BLB"

    # ImportHelper mixin class uses this
    filename_ext = ".blb"

    filter_glob = StringProperty(
            default="*.blb",
            options={'HIDDEN'},
            )

    axis_forward = EnumProperty(
            name="Forward",
            items=(('1', "-Y Forward", ""),
                   ('0', "-X Forward", ""),
                   ('3', "Y Forward", ""),
                   ('2', "X Forward", ""),

                   ),
            default='1',
            )

    shadeless = BoolProperty(
            name="Shadeless Materials",
            description="Applys shadeless to materials",
            default=True,
            )
    
    def execute(self, context):
        from . import import_blb
        import_blb.ImportBLB(self.filepath, self.shadeless, self.axis_forward)
        return {'FINISHED'}

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(Import_blb_class.bl_idname, text="Blockland brick (.blb)")


def register():
    bpy.utils.register_class(Import_blb_class)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(Import_blb_class)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
