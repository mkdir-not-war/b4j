from random import choice, random, randint, sample

MAX_ROOMS = 10
MIN_ROOMS = 3
MAX_MULT = 2

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
		self.links = []

class DungeonGraph:
	def __init__(self):
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
	Furthermore, the order of each depth's list should be such that
	it minimizes distance between connected rooms. E.g., if A -> B,
	then:

	0: [A D C]
	1: [B Y Z]

	is preferable to

	0: [C D A]
	1: [B Y Z]

	'''
	def build_layout(self):
		start = self.nodes['start']
		visited = ['start']
		self.layout[0] = [start]
		rooms = [start]
		nextrooms = start.links
		depth = 1

		# build out preliminary, unorganized layout
		while(len(nextrooms) > 0):
			self.layout[depth] = []
			rooms = [self.nodes[r] for r in nextrooms]
			visited.extend(nextrooms)
			nextrooms = []
			for room in rooms:
				self.layout[depth].append(room)
				for nextroom in room.links:
					if nextroom not in visited and nextroom not in nextrooms:
						nextrooms.append(nextroom)
			depth += 1
		self.maxdepth = depth-1
		print(depth)

	def set_key(self):
		keyroom = choice(self.layout[self.maxdepth])
		self.nodes[keyroom.name].tag = 'key'
		print('%s set to key' % keyroom.name)

	def clear(self):
		self.nodes = {}

	def generate(self, weights):
		start = DungeonNode('start')
		self.node_append(start)

		# build rooms out
		options = ['skip', 'loop', 'append', 'connect']
		weights = weights
		visited = []
		rooms = ['start']
		numrooms = 0
		while (len(rooms) > 0 and numrooms < (MAX_ROOMS - MAX_MULT)):
			room = self.nodes[rooms.pop(0)]
			visited.append(room.name)

			# choose options
			opt = weighted_choice(options, weights)

			# pick again if "connect" and not enough visited rooms
			lenv = len(visited)
			while ((opt == 'connect' and lenv < MAX_MULT) or (opt == 'skip' and lenv < MIN_ROOMS)):
				opt = weighted_choice(options, weights)

			if opt == 'skip':
				continue


			# choose a multiplier for the option
			mult = randint(1, MAX_MULT)

			# add on new rooms for the other options
			if opt == 'loop':
				# create a chain of rooms, length mult+1, that leads back to the current room
				print('loop %s %d' % (room.name, mult))
				prevroom = room
				looplen = mult+1
				for i in range(looplen):
					roomname = 'node %s' % alphaname(numrooms)
					node = DungeonNode(roomname)
					dests = []
					if (i == looplen-1):
						dests = [room]
					self.node_append(node, srcs=[prevroom], dests=dests)
					prevroom = node
					numrooms += 1
					rooms.append(roomname)
			elif opt == 'append':
				# add a number (mult) of additional rooms branching off of the current room
				print('append %s %d' % (room.name, mult))
				for i in range(mult):
					roomname = 'node %s' % alphaname(numrooms)
					node = DungeonNode(roomname)
					self.node_append(node, srcs=[room])
					numrooms += 1
					rooms.append(roomname)
			elif opt == 'connect':
				# connect this room back to a number (mult) of visited rooms
				print('connect %s %d' % (room.name, mult))
				samplelist = list(self.nodes)[:]
				samplelist.remove(room.name)
				for link in room.links:
					samplelist.remove(link)
				prevrooms = sample(samplelist, min(mult, len(samplelist)))
				for pname in prevrooms:
					p = self.nodes[pname]
					room.links.insert(0, pname)
					p.links.append(room.name)

		# organize rooms by depth
		self.build_layout()

		# put key in deepest room of this level
		self.set_key()

		# put locked door somewhere in the dungeon, followed by "end"
		lock = DungeonNode('lock')
		lock.tag = 'lock'
		end = DungeonNode('end')

		self.node_append(lock, srcs=[choice(list(self.nodes.values()))])
		self.node_append(end, srcs=[lock])

	def print(self):
		print()
		print('\tDungeon:')

		for depth in range(self.maxdepth+1):
			print('\t%d. %s' % (depth, [node.name for node in self.layout[depth]]))

def main():
	print('Starting dungeon gen. Enter \'q\' to quit.')
	dungeon = DungeonGraph()
	while(1):
		rin = input('>> ')

		# skip, loop, append, connect
		weights = [80, 20, 10, 20]

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