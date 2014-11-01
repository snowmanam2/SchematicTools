import nbt.nbt as nbt
import copy

class Schematic:
	def __init__(self, filename=None):
		if filename:
			self.load_from_file(filename)
		else:
			self.size_x = 0
			self.size_y = 0
			self.size_z = 0
			self.blocks = bytearray()
			self.data = bytearray()
			self.entities = nbt.TAG_List(type=nbt.TAG_Compound)
			self.tileentities = nbt.TAG_List(type=nbt.TAG_Compound)
	def load_from_file (self, filename):
		nbtfile = nbt.NBTFile(filename)
		
		self.size_x = nbtfile["Width"].value
		self.size_y = nbtfile["Height"].value
		self.size_z = nbtfile["Length"].value
		
		self.blocks = nbtfile["Blocks"].value
		self.data = nbtfile["Data"].value
		self.entities= nbtfile["Entities"]
		if self.entities == None:
			self.entities = nbt.TAG_List(type=nbt.TAG_Compound)
		self.tileentities= nbtfile["TileEntities"]
		if self.tileentities == None:
			self.tileentities = nbt.TAG_List(type=nbt.TAG_Compound)
	def init_sized (self, size_x, size_y, size_z):
		self.size_x = size_x
		self.size_y = size_y
		self.size_z = size_z
		
		data_len = self.size_x * self.size_y * self.size_z

		self.blocks = bytearray(data_len)
		self.data = bytearray(data_len)
		self.entities = nbt.TAG_List(type=nbt.TAG_Compound)
		self.tileentities = nbt.TAG_List(type=nbt.TAG_Compound)

	def get_offset (self, x, y, z):
		offset_y = y * self.size_z * self.size_x
		offset_z = z * self.size_x
		
		return offset_y + offset_z + x
		
	def place_child (self, child, cx, cy, cz):
		max_x = min (child.size_x, self.size_x - cx)
		max_y = min (child.size_y, self.size_y - cy)
		max_z = min (child.size_z, self.size_z - cz)
	
		min_x = max (0, -cx)
		min_y = max (0, -cy)
		min_z = max (0, -cz)
	
		for y in range(min_y, max_y):
			for z in range (min_z, max_z):
				offset = self.get_offset (cx, y + cy, z + cz)
				coffset = child.get_offset (0, y, z)
				
				self.blocks[offset+min_x : offset+max_x] = child.blocks[coffset+min_x : coffset+max_x]
				self.data[offset+min_x : offset+max_x] = child.data[coffset+min_x : coffset+max_x]
		for entity in child.entities:
			pos = entity["pos"]
			ex = pos["x"].value + cx
			ey = pos["y"].value + cy
			ez = pos["z"].value + cz
			
			if 0 <= ex < self.size_x and 0 <= ey < self.size_y and 0 <= ez < self.size_z:
				tempent = copy.deepcopy(entity)
				temppos = tempent["pos"]
				temppos["x"].value = ex
				temppos["y"].value = ey
				temppos["z"].value = ez
				
				self.entities.append (tempent)
		for entity in child.tileentities:
			ex = entity["x"].value + cx
			ey = entity["y"].value + cy
			ez = entity["z"].value + cz
			
			if 0 <= ex < self.size_x and 0 <= ey < self.size_y and 0 <= ez < self.size_z:
				tempent = copy.deepcopy(entity)
				tempent["x"].value = ex
				tempent["y"].value = ey
				tempent["z"].value = ez
				
				self.tileentities.append (tempent)
	def write_to_file (self, filename):
		nbtfile = nbt.NBTFile()
		
		nbtfile.name = "Schematic"
		nbtfile["Width"] = nbt.TAG_Short (value=self.size_x)
		nbtfile["Height"] = nbt.TAG_Short (value=self.size_y)
		nbtfile["Length"] = nbt.TAG_Short (value=self.size_z)
		nbtfile["Materials"] = nbt.TAG_String (value="Alpha")
		nbtfile["Blocks"] = nbt.TAG_Byte_Array ()
		nbtfile["Blocks"].value = self.blocks
		nbtfile["Data"] = nbt.TAG_Byte_Array ()
		nbtfile["Data"].value = self.data
		nbtfile["Entities"] = self.entities
		nbtfile["TileEntities"] = self.tileentities
		
		nbtfile.write_file (filename)

