# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Main File containing the important definitions

from . import mrw_g2_filesystem, mrw_g2_glm, mrw_g2_gla
import bpy

def findSceneRootObject():
    scene_root = None
    if "scene_root" in bpy.data.objects:
        # if so, use that
        scene_root = bpy.data.objects["scene_root"]
    return scene_root

class Scene:
    scale = 1.0
    glm = None
    gla = None
    basepath = ""
    
    def __init__(self, basepath):
        self.basepath = basepath
    
    # Fills scene from on GLM file
    def loadFromGLM(self, glm_filepath_rel):
        success, glm_filepath_abs = mrw_g2_filesystem.FindFile(glm_filepath_rel, self.basepath, ["glm"])
        if not success:
            print("File not found: ", self.basepath + glm_filepath_rel + ".glm", sep="")
            return False, "File not found! (no .glm?)"
        self.glm = mrw_g2_glm.GLM()
        success, message = self.glm.loadFromFile(glm_filepath_abs)
        if not success:
            return False, message
        return True, ""
    
    # Loads scene from on GLA file
    def loadFromGLA(self, gla_filepath_rel, loadAnimations=False):
        # create default skeleton if necessary (doing it here is a bit of a hack)
        if gla_filepath_rel == "*default":
            self.gla = mrw_g2_gla.GLA()
            self.gla.isDefault = True
            return True, ""
        success, gla_filepath_abs = mrw_g2_filesystem.FindFile(gla_filepath_rel, self.basepath, ["gla"])
        if not success:
            print("File not found: ", self.basepath + gla_filepath_rel + ".gla", sep="")
            return False, "File not found! (no .gla?)"
        self.gla = mrw_g2_gla.GLA()
        success, message = self.gla.loadFromFile(gla_filepath_abs)
        if not success:
            return False, message
        return True, ""
    
    # "Loads" model from Blender data
    def loadModelFromBlender(self, glm_filepath_rel, gla_filepath_rel):
        scene_root = findSceneRootObject()
        if not scene_root:
            return False, "No scene_root object found!"
        self.glm = mrw_g2_glm.GLM()
        success, message = self.glm.loadFromBlender(glm_filepath_rel, gla_filepath_rel, self.basepath, scene_root)
        if not success:
            return False, message
        return True, ""
    
    # "Loads" skeleton & animation from Blender data
    def loadSkeletonFromBlender(self, gla_filepath_rel):
        scene_root = findSceneRootObject()
        if not scene_root:
            return False, "No scene_root object found!"
        self.gla = mrw_g2_gla.GLA()
        success, message = self.gla.loadFromBlender(gla_filepath_rel, scene_root)
        if not success:
            return False, message
        return True, ""
    
    #saves the model to a .glm file
    def saveToGLM(self, glm_filepath_rel):
        glm_filepath_abs = mrw_g2_filesystem.AbsPath(glm_filepath_rel, self.basepath) + ".glm"
        success, message = self.glm.saveToFile(glm_filepath_abs)
        if not success:
            return False, message
        return True, ""
    
    # saves the skeleton & animations to a .gla file
    def saveToGLA(self, gla_filepath_rel):
        gla_filepath_abs = mrw_g2_filesystem.AbsPath(gla_filepath_rel, self.basepath) + ".gla"
        success, message = self.gla.saveToFile(gla_filepath_abs)
        if not success:
            return False, message
        return True, ""
    
    # "saves" the scene to blender
    def saveToBlender(self, scale):
        #is there already a scene root in blender?
        scene_root = findSceneRootObject()
        if scene_root:
            # make sure it's linked to the current scene
            if not "scene_root" in bpy.context.scene.objects:
                bpy.context.scene.objects.link(scene_root)
        else:
            # create it otherwise
            scene_root = bpy.data.objects.new("scene_root", None)
            scene_root.scale = (scale, scale, scale)
            bpy.context.scene.objects.link(scene_root)
        # there's always a skeleton (even if it's *default)
        success, message = self.gla.saveToBlender(scene_root)
        if not success:
            return False, message
        if self.glm:
            success, message = self.glm.saveToBlender(self.basepath, self.gla, scene_root)
            if not success:
                return False, message
        return True, ""
    
    # returns the relative path of the gla file referenced in the glm header
    def getRequestedGLA(self):
        return self.glm.getRequestedGLA()