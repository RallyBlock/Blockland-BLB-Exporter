import os
import bpy, bmesh

def Vec3Dist(a, b):
	return abs((a[0]-b[0]) + (a[1]-b[1]) + (a[2]-b[2]))

def AddFace(bmesh, POS1, POS2, POS3, POS4, N1, N2, N3, N4):
	POS1 = ( float(POS1[0]) , float(POS1[1]) , (float(POS1[2])/2.5) )
	POS2 = ( float(POS2[0]) , float(POS2[1]) , (float(POS2[2])/2.5) )
	POS3 = ( float(POS3[0]) , float(POS3[1]) , (float(POS3[2])/2.5) )
	POS4 = ( float(POS4[0]) , float(POS4[1]) , (float(POS4[2])/2.5) )
	
	Vert1 = bmesh.verts.new(POS1)
	Vert2 = bmesh.verts.new(POS2)
	Vert3 = bmesh.verts.new(POS3)
	Vert4 = bmesh.verts.new(POS4)
	
	Vert1.normal = ( float(N1[0]), float(N1[1]), float(N1[2]) )
	Vert2.normal = ( float(N2[0]), float(N2[1]), float(N2[2]) )
	Vert3.normal = ( float(N3[0]), float(N3[1]), float(N3[2]) )
	Vert4.normal = ( float(N4[0]), float(N4[1]), float(N4[2]) )
	
	NewFace = bmesh.faces.new( (Vert1,Vert2,Vert3,Vert4) )
	
	maxdist = 0.001
	if Vec3Dist(Vert1.normal, Vert2.normal)>maxdist or Vec3Dist(Vert2.normal, Vert3.normal)>maxdist or Vec3Dist(Vert3.normal, Vert4.normal)>maxdist:
		NewFace.smooth = True
	
	return NewFace

def AddUV(NewFace, UV1, UV2, UV3, UV4, Layer, Tex):
	UV1 = ( float(UV1[0]) , 1 - (float(UV1[1])) )
	UV2 = ( float(UV2[0]) , 1 - (float(UV2[1])) )
	UV3 = ( float(UV3[0]) , 1 - (float(UV3[1])) )
	UV4 = ( float(UV4[0]) , 1 - (float(UV4[1])) )
	
	NewFace.loops[0][Layer].uv = ( UV1[0] , UV1[1] )
	NewFace.loops[1][Layer].uv = ( UV2[0] , UV2[1] )
	NewFace.loops[2][Layer].uv = ( UV3[0] , UV3[1] )
	NewFace.loops[3][Layer].uv = ( UV4[0] , UV4[1] )
	
	return NewFace

def AddTex(Tex): # final command
    if bpy.data.textures.find(Tex) == -1:

        abs_path = os.path.dirname(__file__)
        if Tex == 'PRINT':
            path = os.path.join(abs_path, 'textures/spraycanlabel.png')
        else:
            path = os.path.join(abs_path, 'textures/brick' +Tex+ '.png')

        image = bpy.data.images.load(path)
        text = bpy.data.textures.new(Tex, 'IMAGE')
        text.image = image
        text.image.use_fields = False

        if Tex == 'SIDE':
            text.extension = 'EXTEND'

    return

def GetMatName(Tex, Color):
	
	if Color=="None":
		name = Tex + " BLANK"
	else:
		tokens = ""
		if float(Color[3])<0:
			if float(Color[0])<0:
				tokens += " CSUB"
			else:
				tokens += " CADD"
		name = Tex+" ["+Color[0][0:5]+" "+Color[1][0:5]+" "+Color[2][0:5]+" "+Color[3][0:5]+"]" + tokens
	
	return name

def AddMat(shadeless, obj, Tex, norm, Color):
	
	name = GetMatName(Tex, Color)
	
	bpyCount = bpy.data.materials.find(name)
	objCount = obj.data.materials.find(name)
	
	if(bpyCount > -1):
		if(bpy.data.materials[bpyCount].use_shadeless != shadeless):
			bpy.data.materials[bpyCount].use_shadeless = shadeless
		
		if(objCount == -1):
			obj.data.materials.append(bpy.data.materials[bpyCount])
		
		return
	
	mat = bpy.data.materials.new(name)
	mat.use_shadeless = shadeless
	
	mtex = mat.texture_slots.add()
	mtex.texture = bpy.data.textures[bpy.data.textures.find(Tex)]
	mtex.texture_coords = "UV"
	
	if(Color == "None"):
		mat.diffuse_color = (0.5, 0.5, 0.5)
	else:
		mat.use_transparency = True
		
		#mat.diffuse_color = (float(Color[0]), float(Color[1]), float(Color[2]))
		#mat.alpha = float(Color[3]) if float(Color[3]) > 0 else -float(Color[3])
		
		mat.diffuse_color = (abs(float(Color[0])), abs(float(Color[1])), abs(float(Color[2])))
		mat.alpha = abs(float(Color[3]))
	
	obj.data.materials.append(mat)
	
	return

def SetMat(obj, NewFace, Tex, norm, Color):
	
	name = GetMatName(Tex, Color)
	
	if Color == "None":
		MCount = obj.data.materials.find(name)
	else:
		MCount = obj.data.materials.find(name)
	
	NewFace.material_index = MCount
	
	return

def ImportBLB(filePath, shadeless, axis_forward):
	import os
	import bpy, bmesh
	
	file = open(filePath)
	
	line = file.readline()
	line = file.readline()
	
	if line == "BRICK":
		return {"Brick importer does not handle cubic type"}
	
	BrickName = (os.path.splitext(os.path.basename(filePath))[0])
	
	# Blender properties
	bpy.context.scene.game_settings.material_mode = "GLSL"
	
	# mesh, obj
	mesh = bpy.data.meshes.new(BrickName + "_m") 
	obj = bpy.data.objects.new(BrickName, mesh)
	obj.show_transparent = True
	bpy.context.scene.objects.link(obj)
	
	# bmesh
	global bmesh
	bmesh = bmesh.new()
	bmesh.from_mesh(mesh)
	Layer = bmesh.loops.layers.uv.new()
	
	while line:
		if "TEX:" in line:
			Tex = line.replace("TEX:","").replace("\n","")
			
			AddTex(Tex)
			
			POSH = file.readline().replace("\n","") #Position Header
			POS1 = (" ".join(file.readline().split())).split()
			POS2 = (" ".join(file.readline().split())).split()
			POS3 = (" ".join(file.readline().split())).split()
			POS4 = (" ".join(file.readline().split())).split()
			
			UVH = file.readline().replace("\n","") # UV Header
			UV1 = (" ".join(file.readline().split())).split()
			UV2 = (" ".join(file.readline().split())).split()
			UV3 = (" ".join(file.readline().split())).split()
			UV4 = (" ".join(file.readline().split())).split()
			
			C1 = "None"
			
			CNH = file.readline().replace("\n","") # Color or Normal Header
			
			if CNH == "COLORS:":
				C1 = (" ".join(file.readline().split())).split()
				C2 = (" ".join(file.readline().split())).split()
				C3 = (" ".join(file.readline().split())).split()
				C4 = (" ".join(file.readline().split())).split()
				CNH = file.readline().replace("\n","") # Normal Header
			
			N1 = (" ".join(file.readline().split())).split()
			N2 = (" ".join(file.readline().split())).split()
			N3 = (" ".join(file.readline().split())).split()
			N4 = (" ".join(file.readline().split())).split()
			
			NewFace = AddFace(bmesh, POS1, POS2, POS3, POS4, N1, N2, N3, N4)
			NewFace = AddUV(NewFace, UV1, UV2, UV3, UV4, Layer, Tex)
			
			AddMat(shadeless, obj, Tex, N1, C1)
			SetMat(obj, NewFace, Tex, N1, C1)
		
		try:
			line = file.readline()
		except StopIteration:
			break
	
	file.close()
	bmesh.to_mesh(mesh)
	
	bpy.ops.object.select_all(action="DESELECT")
	obj.select = True
	bpy.context.scene.objects.active = obj
	
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_all(action="TOGGLE")
	#bpy.ops.mesh.normals_make_consistent(inside=True)
	bpy.ops.mesh.flip_normals()
	bpy.ops.mesh.remove_doubles()
	bpy.ops.mesh.select_all(action="TOGGLE")
	bpy.ops.object.mode_set(mode="OBJECT")
	
	bpy.ops.transform.rotate(value=((-1.5708)*float(axis_forward)))
	bpy.ops.object.transform_apply(rotation=True)
	
	return {"FINISHED"}
