
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

#change this to your username FIXME
pedanticaPath="/home/robin/pedantica/"
entitiesPath=pedanticaPath+"tools/editor/entities/"

initialized=False

class Entity:
	'Entity class for all move:able entitys in a level, loaded from separate blend files'
	def __init__(self,title,name,blendFile):
		self.title=title #title is the pronounced entity name in english
		self.name=name #name is the collapsed entity name
		self.blendFile=blendFile #blendFile is the filename containing the entity


def checkInitialized():
	global initialized

	if initialized is True:
		return
	else:
		#THE LIST OF ALL ENTITIES AVAILABLE TO THE USER
		entities=[]

		#ADD THE ENTITIES THAT ARE IN THE ENTITIES FOLDER
		entities.append(Entity("a Flying Enemy","EnemyFlying","EnemyFlying.blend"))

		#LOAD ALL ENTITY MESHES FROM EXTERNAL FILES
		for e in entities:
			filepath=entitiesPath+e.blendFile

			with bpy.data.libraries.load(filepath,True) as (data_from, data_to):
				data_to.groups = data_from.groups


		initialized=True

def addEntity(entityName):
	checkInitialized()

	instanceName=""
	done=False

	while not done:
		instanceName=entityName+"."+str(randint(1,999))

		for i in str(bpy.data.objects[:-1]):
			if instanceName in i:
				continue
			else:
				done=True
				break

	bpy.ops.object.empty_add(type="PLAIN_AXES")
	bpy.data.objects["Empty"].name=instanceName
	bpy.data.objects[instanceName].dupli_type="GROUP"
	bpy.data.objects[instanceName].dupli_group=bpy.data.groups[entityName]


class add_flying_enemy(bpy.types.Operator):
	'''Adds a Flying Enemy to the current scene'''
	bl_idname = "mesh.enemy_flying_add"
	bl_label = "Add"+" a Flying Enemy"

	def execute(self, context):
		addEntity("EnemyFlying")

		return {'FINISHED'}


#EXPORT PEDANTICA LEVEL TO FILE
class export_leveldata(bpy.types.Operator):
	'''Exports the current scene as a Pedantica level'''
	bl_idname = "mesh.export_pedantica_level"
	bl_label = "Export Pedantica Level"

	def execute(self, context):
		levelFilename=pedanticaPath+"engine/assets/maps/prison02.level"

		#HIDE ENEMIES
		for o in bpy.data.objects:
			if "EnemyFlying." in str(o):
				o.hide=True

		#EXPORT STATIC MESH AS OBJ
		bpy.ops.export_scene.obj(filepath=levelFilename,use_triangles=True)

		#UNHIDE ENEMIES
		for o in bpy.data.objects:
			if "EnemyFlying." in str(o):
				o.hide=False

		#BEGIN WRITE FILE
		with open(levelFilename,"a") as f:
			f.write('''
# END OF LEVEL MESH

# BEGIN LEVEL ENTITIES

Entity models/sink.obj 3.0 0.5 1.0
Entity models/lv1.obj 0.0 0.0 0.0
Entity models/lv1-wall.obj 20.0 20.0 0.0
Entity models/lv1-wall-full.obj 20.0 20.0 0.0
Entity models/key_old.obj 20.0 20.0 0.0
Entity models/key_complex.obj 20.0 20.0 0.0
Entity models/door-old-key.obj 20.0 20.0 0.0
Entity models/door-complex-key.obj 20.0 20.0 0.0
Entity models/floor.obj 20.0 0.0 0.0
Entity models/floor5.obj 20.0 0.0 0.0
Entity models/traffic_light_pedestrian.obj 5.0 4.0 5.0
Entity models/mask_guy.obj 1.0 4.0 5.0
Entity models/colt25.obj 0.0 0.0 0.0
Entity models/gun_shot.obj 0.0 0.0 0.0
Entity models/gun.obj 0.0 0.0 0.0
Entity models/knife.obj 0.0 0.0 0.0
Entity models/gun_display.obj 0.0 0.0 0.0

//music audio/dark-clouds.flac

# BEGIN LEVEL ENEMYS

# Define flying enemy before using it
Entity models/tentacle.obj 24.0 3.0 0.0
Entity models/flyingenemy-spikes.obj 21.0 3.0 2.0
''')

			#APPEND ENEMY POSITIONS
			for o in bpy.data.objects:
				if "EnemyFlying." in str(o):
					f.write("EnemyFlying "+o.name+" ")
					loc=o.location*bpy_extras.io_utils.axis_conversion(to_forward='Z',to_up='Y')	
					f.write(str(loc.x)+" "+str(loc.y)+" "+str(loc.z)+" ")
					rot=mathutils.Vector(o.rotation_euler)
					rot=rot*bpy_extras.io_utils.axis_conversion(to_forward='Z',to_up='Y')
					f.write(str(rot.x)+" "+str(rot.y)+" "+str(rot.z))
					f.write("\n")

		return {'FINISHED'}


#
#    Registration
#

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()

