"""
	Create atlas from images, using PIL(python image library).
	Idea taken from http://blackpawn.com/texts/lightmaps/
"""


import math
from PIL import Image

PADDING = 1

class Rect:
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

class AtlasNode:
	def __init__(self):
		self.first_child = None
		self.second_child = None
		self.rect = None
		self.image = None
		
	def has_enough_space(self, image):
		rect = self.rect
		image_size = image.size
		
		return rect.width >= image_size[0] and rect.height >= image_size[1]
		
	def is_perfectly_fit(self, image):
		rect = self.rect
		image_size = image.size
		
		return rect.width == image_size[0] and rect.height == image_size[1]
		
	def insert(self, image):
		if self.first_child != None:
			new_node = self.first_child.insert(image)
			if new_node == None:
				return self.second_child.insert(image)
			
			return new_node
		
		if self.image != None or not self.has_enough_space(image):
			return None
		
		if self.is_perfectly_fit(image):
			self.image = image
			return self
		
		first_child = AtlasNode()
		second_child = AtlasNode()
		self.first_child = first_child
		self.second_child = second_child
		
		rect = self.rect
		image_width = image.size[0]
		image_height = image.size[1]
		
		width_diff = rect.width - image_width
		height_diff = rect.height - image_height
		
		if width_diff > height_diff:
			first_child.rect = Rect(rect.x, rect.y, image_width, rect.height)
			second_child.rect = Rect(rect.x + image_width + PADDING, rect.y, rect.width - image_width - PADDING, rect.height)
		else:
			first_child.rect = Rect(rect.x, rect.y, rect.width, image_height)
			second_child.rect = Rect(rect.x, rect.y + image_height + PADDING, rect.width, rect.height - image_height - PADDING)
		
		return self.first_child.insert(image)
		
	def merge_to(self, target):
		if self.first_child != None:
			self.first_child.merge_to(target)
			self.second_child.merge_to(target)
		
		if self.image != None:
			rect = self.rect
			target.paste(self.image, (rect.x, rect.y, rect.x + rect.width,  rect.y + rect.height))
				

def calc_atlas_width(image_list):
	area_sum = 0
	max_image_length = 0
	for image in image_list:
		area_sum += image.size[0] * image.size[1]
		max_image_length = max(max_image_length, max(image.size[0], image.size[1]))


	length = int(math.ceil(math.sqrt(area_sum)))
		
	return max(length, max_image_length)

def create_atlas(images_path_list):
	image_list = []
	for image_path in images_path_list:
		image = Image.open(image_path)
		image_list.append(image)
	
	def sort_func(lhs, rhs):
		if lhs.size[0] + lhs.size[1] <= rhs.size[0] + rhs.size[1]:
			return 1
		
		return -1
	
	image_list.sort(sort_func)
	
	count = 0
	def create(image_list, count):
		root = AtlasNode()
		width = calc_atlas_width(image_list)
		root.rect = Rect(0, 0, width, width)
		
		remain_image_list = []
		
		for image in image_list:
			if root.insert(image) == None:
				remain_image_list.append(image)
				
		target = Image.new('RGBA', (width, width))
		root.merge_to(target)
		count += 1
		target.save('atlas' + str(count) + '.png')
			
		if len(remain_image_list) > 0:
			create(remain_image_list, count)
	
	create(image_list, count)
		
