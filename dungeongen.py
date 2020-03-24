from random import choice, random, randint, sample

MAX_SECTIONS = 8
MIN_SECTIONS = 1
MAX_ROOMS = 10
MIN_ROOMS = 3

def weighted_choice(options, weights):
	summed = sum(weights)
	weights = [w/summed for w in weights]

	r = random()
	counter = 0.0
	for index in range(len(weights)):
		counter += weights[index]
		if counter > r:
			return options[index]
	assert(False)

def alphaname(num):
	result = ''
	if (num > 26):
		result = chr((num//26)+65) + chr((num%26)+65)
	else:
		result = chr((num%26)+65)
	return result

class DungeonNode:
	# nodetypes: room, intersection, lock
	# tags: start, end, key
	def __init__(self, name=''):
		self.name = name
		self.tag = ''
		self.locked = False
		self.links = []
		self.depth = -1

class DungeonGraph:
	def __init__(self):
		self.clear()

	def clear(self):
		self.nodes = {}
		self.layout = {}
		self.maxdepth = 0

	def node_append(self, node, srcs=[], dests=[]):
		for src in srcs:
			node.links.insert(0, src.name)
			src.links.insert(0, node.name)
		for dest in dests:
			node.links.insert(0, dest.name)
			dest.links.insert(0, node.name)
		self.nodes[node.name] = node

	'''
	After the graph has been generated, organize into lists by depth.
	'''
	def build_layout(self, start):
		# set current depth
		if (start.depth == 0):
			self.layout[0] = [start]
		rooms = [start]
		nextrooms = [self.nodes[link] for link in start.links]
		depth = start.depth + 1

		# build layout
		while(len(nextrooms) > 0):
			# if current depth is further than before, set up the layout list
			if (depth not in self.layout):
				self.layout[depth] = []
			
			# swap room buffer
			rooms = nextrooms[:]
			nextrooms = []
			# if room is new (depth=-1), put it in the layout
			for room in rooms:
				if (room.depth < 0):
					room.depth = depth
					self.layout[depth].append(room)
					for nextroom in room.links:
						node = self.nodes[nextroom]
						if node.depth < 0 and node not in nextrooms:
							nextrooms.append(node)
			if (len(nextrooms) > 0):
				depth += 1

		i = 0
		while (i in self.layout):
			nodes = self.layout[i]
			if (len(nodes) > 0):
				i += 1
			else:
				del self.layout[i]
				break
		self.maxdepth = i-1


	def set_key(self, section):
		keyroom = self.layout[self.maxdepth][0]
		if (section > 1):
			while (keyroom.tag == 'key'):
				keyroom = choice(list(self.nodes.values()))
		self.nodes[keyroom.name].tag = 'key'
		#print('%s set to key' % keyroom.name)

	def set_locked_nodes(self, section):
		room = choice(list(self.nodes.values()))
		while (room.tag == 'key'):
			room = choice(list(self.nodes.values()))
		
		end = DungeonNode('%s' % alphaname(len(self.nodes.keys())-1))
		end.locked = True
		end.depth = room.depth + 1

		self.node_append(end, srcs=[room])

		if end.depth in self.layout:
			self.layout[end.depth].append(end)
		else:
			self.layout[end.depth] = [end]
			self.maxdepth += 1

	def generate(self, weights):
		start = DungeonNode('start')
		start.tag = 'start'
		start.depth = 0
		self.node_append(start)

		# build rooms out
		options = ['skip', 'loop', 'append', 'connect']
		weights = weights
		visited = []
		sections = randint(MIN_SECTIONS, MAX_SECTIONS)

		totalrooms = 0
		numrooms = 0
		for section in range(1, sections+1):
			rooms = [start.name]

			totalrooms += numrooms
			numrooms = 0
			while (len(rooms) > 0 and numrooms < MAX_ROOMS):
				room = self.nodes[rooms.pop(0)]
				if (room.name not in visited):
					visited.append(room.name)

				# choose options
				opt = weighted_choice(options, weights)

				# pick again if "connect" and not enough visited rooms
				lenv = len(visited) - 1
				while ((opt == 'connect'  or opt == 'skip') and lenv < MIN_ROOMS):
					opt = weighted_choice(options, weights)

				if opt == 'skip':
					continue


				# add on new rooms for the other options
				if opt == 'loop':
					# create a chain of rooms, length mult+1, that leads back to the current room
					#print('loop %s %d' % (room.name, mult))
					prevroom = room
					for i in range(2):
						roomname = '%s' % alphaname(numrooms+totalrooms)
						node = DungeonNode(roomname)
						dests = []
						if (i == 1):
							dests = [room]
						self.node_append(node, srcs=[prevroom], dests=dests)
						prevroom = node
						numrooms += 1
						rooms.append(roomname)
				elif opt == 'append':
					# add a number (mult) of additional rooms branching off of the current room
					#print('append %s %d' % (room.name, mult))
					roomname = '%s' % alphaname(numrooms+totalrooms)
					node = DungeonNode(roomname)
					self.node_append(node, srcs=[room])
					numrooms += 1
					rooms.append(roomname)
				elif opt == 'connect':
					# connect this room back to a number (mult) of visited rooms
					#print('connect %s %d' % (room.name, mult))
					samplelist = list(self.nodes)[:]
					samplelist.remove(room.name)
					for link in room.links:
						samplelist.remove(link)
					prevrooms = sample(samplelist, min(1, len(samplelist)))
					for pname in prevrooms:
						p = self.nodes[pname]
						room.links.insert(0, pname)
						p.links.append(room.name)

			# organize rooms by depth
			self.build_layout(start)

			# put key in deepest room of this level
			self.set_key(section)

			# put locked door somewhere in the dungeon, followed by "end"
			self.set_locked_nodes(section)
			numrooms += 1

			# pick a new starting position for the next section
			start = choice(list(self.nodes.values()))

	def print(self):
		print()
		print('\tDungeon:')

		linelength = 19

		for depth in range(self.maxdepth, -1, -1):
			nodes = self.layout[depth]
			topline = '\t%d. ' % depth
			for node in nodes:
				line = ''
				if (node.tag in ['key']):
					line = '%s (%s)' % (node.name, node.tag)
				else:
					line = '%s' % node.name
				if (node.locked):
					line += ' (lock)'
				line += ' ' * (max(0 , linelength - len(line)))
				topline += '%s' % line
			print()
			print(topline)

			maxlinks = max([len(node.links) for node in nodes])
			for i in range(maxlinks):
				printline = '\t   '
				for node in nodes:
					if len(node.links) > i:
						link = self.nodes[node.links[i]]
						line = '%s' % link.name
						line += ' ' * (max(0 , linelength - 5 - len(line)))
						printline += '|--> %s' % line
					else:
						printline += ' ' * linelength
				print(printline)

def main():
	print('Starting dungeon gen. Enter \'q\' to quit.')
	dungeon = DungeonGraph()
	while(1):
		rin = input('>> ')

		# skip, loop, append, connect
		weights = [80, 20, 25, 5]

		if (rin == 'q'):
			return
		elif (len(rin) > 0):
			vals = []
			try:
				vals = [float(v) for v in rin.split(' ')]
				if len(vals) == 4:
					weights = vals[:]
			except:
				print('Malformed weights -- using defaults.')

		dungeon.generate(weights)
		dungeon.print()
		dungeon.clear()



if __name__ == '__main__':
	main()