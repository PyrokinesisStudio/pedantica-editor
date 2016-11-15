'''
	pedantica-editor blender plugin
	Copyright (C) 2016  Robin Stjerndorff - robin@stjerndorff.org

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import bpy

#
#    Edit/export a pedantica .blend-level with this pedantica editor plugin
#

#
#    User interface
#

from bpy.props import *
import bpy_extras
import mathutils
from random import randint
import getpass #for getuser

#for finding entity files
from os import listdir
from os.path import isfile, join, splitext

#change this to reflect automatically correct pedantica path FIXME
pedanticaPath="/home/"+getpass.getuser()+"/pedantica/"
entitiesPath=pedanticaPath+"tools/pedantica-editor/entities/"
staticentitiesPath=entitiesPath+"static/"

initialized=False

class Entity:
	'Entity class for all movable entitys in a level, loaded from separate blend files'
	def __init__(self,title,name,blendFile):
		self.title=title #title is the pronounced entity name in english
		self.name=name #name is the entity name abbreviation
		self.blendFile=blendFile #blendFile is the filename containing the entity

#THE LIST OF ALL ENTITIES AVAILABLE
entities=[]

def checkInitialized():
	global initialized
	global entities

	if initialized is True:
		return
	else:

		#ADD THE ENTITIES THAT ARE IN THE STATIC ENTITIES FOLDER
		entityBlendFiles = [f for f in listdir(staticentitiesPath) if isfile(join(staticentitiesPath, f)) and f.endswith(".blend")]

		#Add entities: description, filename without ending, filename
		for e in entityBlendFiles:
			entities.append(Entity("Some description",splitext(e)[0],join(staticentitiesPath, e)))

		#ADD ENEMY
		entities.append(Entity("a Flying Enemy","EnemyFlying",entitiesPath+"EnemyFlying.blend"))

		#LOAD ALL ENTITY MESHES FROM EXTERNAL FILES
		for e in entities:
			with bpy.data.libraries.load(e.blendFile,True,True) as (data_from, data_to):
				data_to.groups = data_from.groups
				#e.title=data_from.SOMETHING_TITLE_CUSTOM_DATA #FIXME get from .blend file

		initialized=True

def addEntity(entityName):
	checkInitialized()

	instanceName=""
	done=False

	#Generate unique entity name
	while not done:
		instanceName=entityName+"."+str(randint(1,999))

		for i in str(bpy.data.objects[:-1]):
			if instanceName in i:
				continue
			else:
				done=True
				break

	bpy.ops.object.empty_add(type="PLAIN_AXES")
	bpy.context.active_object.name=instanceName
	bpy.data.objects[instanceName].dupli_type="GROUP"
	bpy.data.objects[instanceName].dupli_group=bpy.data.groups[entityName]


class add_flying_enemy(bpy.types.Operator):
	'''Adds a Flying Enemy to the current scene'''
	bl_idname = "mesh.enemy_flying_add"
	bl_label = "Pedantica Add Flying Enemy"

	def execute(self, context):
		addEntity("EnemyFlying")

		return {'FINISHED'}


def fixedLocation(o):
	return o.location*bpy_extras.io_utils.axis_conversion(to_forward='Z',to_up='-Y')

def fixedRotation(o):
	rotation=o.rotation_euler

	return rotation

#EXPORT PEDANTICA LEVEL TO FILE
class export_leveldata(bpy.types.Operator):
	'''Exports the current scene as a Pedantica level'''
	bl_idname = "mesh.export_pedantica_level"
	bl_label = "Pedantica Export Level"


	def execute(self, context):
		levelFilename=pedanticaPath+"engine/assets/maps/prison02.level"

		global entities

		#HIDE ENEMIES/ENTITIES
		for o in bpy.data.objects:
			for e in entities:
				if e.name in str(o.name):
					o.hide=True

		#EXPORT STATIC MESH AS OBJ
		bpy.ops.export_scene.obj(filepath=levelFilename,use_triangles=True,path_mode="STRIP")

		#UNHIDE ENEMIES/ENTITIES
		for o in bpy.data.objects:
			for e in entities:
				if e.name in str(o.name):
					o.hide=False

		#BEGIN TO APPEND MORE DATA TO THE FILE
		with open(levelFilename,"a") as f:
			f.write('''
# END OF LEVEL MESH

//music audio/dark-clouds.flac

''')

			#Write Player Camera Spawn Position
			for o in bpy.data.objects:
				if "PlayerPositionSpawn" in str(o):
					loc=fixedLocation(o)
					rot=fixedRotation(o)
					f.write("PlayerPositionSpawn "+str(loc.x)+" "+str(loc.y)+" "+str(loc.z)+" "+str(rot.z)+" "+str(rot.x))
					break

			f.write('''
# BEGIN LEVEL ENTITIES

''')

			#APPEND ENTITY POSITIONS
			for o in bpy.data.objects:
				for e in entities:
					if e.name in str(o.name) and e.name is not "EnemyFlying":
						#rot=fixedRotation(o)
						#f.write(str(rot.x)+" "+str(rot.y)+" "+str(rot.z))
						loc=fixedLocation(o)
						f.write("Entity models/"+e.name+".obj "+str(loc.x)+" "+str(loc.y)+" "+str(loc.z)+"\n")

			f.write('''
//Entity models/Sink.obj 3.0 0.5 1.0
//Entity models/floor.obj 20.0 0.0 0.0
//Entity models/floor5.obj 20.0 0.0 0.0
//Entity models/TrafficYieldAnarchy.obj 5.0 0.1 5.0
//Entity models/TrafficLight.obj 9.0 0.1 5.0
//Entity models/mask_guy.obj 1.0 4.0 5.0
//Entity models/colt25.obj 0.0 0.0 0.0
//Entity models/knife.obj 0.0 0.0 0.0

Entity models/gun_shot.obj 0.0 0.0 0.0
Entity models/gun.obj 0.0 0.0 0.0
Entity models/gun_display.obj 0.0 0.0 0.0



# Load FlyingEnemy models before using them
Entity models/tentacle.obj 24.0 3.0 0.0
Entity models/flyingenemy-spikes.obj 21.0 3.0 2.0

# BEGIN LEVEL ENEMIES

''')

			#APPEND ENEMY POSITIONS
			for o in bpy.data.objects:
				if "EnemyFlying." in str(o):
					f.write("EnemyFlying "+o.name+" ")
					loc=fixedLocation(o)
					f.write(str(loc.x)+" "+str(loc.y)+" "+str(loc.z)+" ")
					rot=fixedRotation(o)
					f.write(str(rot.x)+" "+str(rot.y)+" "+str(rot.z))
					f.write("\n")

		return {'FINISHED'}



def item_cb(self, context):
	onlyfiles = [splitext(f)[0] for f in listdir(staticentitiesPath) if isfile(join(staticentitiesPath, f)) and f.endswith(".blend")]

	return [(str(i), str(i), "") for i in onlyfiles]


class SimpleOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.simple_operator"
	bl_label = "Pedantica Add Entity"
	bl_property = "my_enum"

	my_enum = bpy.props.EnumProperty(items=item_cb)

	def execute(self, context):
		addEntity(self.my_enum)
		self.report({'INFO'}, "Added: %s" % self.my_enum)

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.invoke_search_popup(self)
		return {'FINISHED'}

#
#    Registration
#

def register():
	bpy.utils.register_module(__name__)
	bpy.utils.register_class(SimpleOperator)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.utils.unregister_class(SimpleOperator)

if __name__ == "__main__":
	register()


