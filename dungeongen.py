from random import choice, random, randint, sample

MAX_ROOMS = 30
MIN_ROOMS = 4
MAX_MULT = 3

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
		self.type = 'room'
		self.previous = []
		self.next = []

	def numlinks(self):
		result = len(self.previous) + len(self.next)
		return result

class DungeonGraph:
	def __init__(self):
		self.nodes = {}

	def node_append(self, node, srcs=[], dests=[]):
		for src in srcs:
			node.previous.append(src.name)
			src.next.insert(0, node.name)
		for dest in dests:
			node.next.insert(0, dest.name)
			dest.previous.append(node.name)
		self.nodes[node.name] = node

	def node_insert(self, node, srcs=[], dests=[]):
		for src in srcs:
			for dest in dests:
				if (dest.name in src.next):
					src.next.remove(dest.name)
					dest.previous.remove(src.name)
		self.node_append(node, srcs, dests)

	def node_collapse(self, node):
		assert(node.type == 'room')
		node.type = 'intersection'

	# doesn't accoutn for loops quite yet
	def set_end(self):
		start = self.nodes['room A']
		depthtracker = {}
		depthtracker['room A'] = 0
		rooms = [start]
		nextrooms = start.next[:]
		depth = 0

		while(len(nextrooms) > 0):
			depth += 1
			rooms = [self.nodes[r] for r in nextrooms]
			nextrooms = []
			for room in rooms:
				depthtracker[room.name] = depth
				for nextroom in room.next:
					if nextroom not in depthtracker:
						nextrooms.append(nextroom)
		end = choice(rooms)
		self.nodes[end.name].tag = 'end'
		print('%s set to end' % end.name)

	def clear(self):
		self.nodes = {}

	def generate(self, weights, collapse_percent):
		start = DungeonNode('room A')
		roomb = DungeonNode('room B')

		self.node_append(start)
		self.node_append(roomb, srcs=[start])

		# build rooms out
		options = ['skip', 'loop', 'append', 'insert', 'connect']
		weights = weights
		visited = []
		rooms = ['room A']
		numrooms = 2
		while (len(rooms) > 0 and numrooms < MAX_ROOMS*(1.0+collapse_percent)):
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
				# create a chain of rooms, length mult, that leads back to the current room
				print('loop %s %d' % (room.name, mult))
				prevroom = room
				for i in range(mult):
					roomname = 'room %s' % alphaname(numrooms)
					node = DungeonNode(roomname)
					dests = []
					if (i == mult-1):
						dests = [room]
					self.node_append(node, srcs=[prevroom], dests=dests)
					prevroom = node
					numrooms += 1
					rooms.append(roomname)
			elif opt == 'append':
				# add a number (mult) of additional rooms branching off of the current room
				print('append %s %d' % (room.name, mult))
				for i in range(mult):
					roomname = 'room %s' % alphaname(numrooms)
					node = DungeonNode(roomname)
					self.node_append(node, srcs=[room])
					numrooms += 1
					rooms.append(roomname)
			elif opt == 'insert':
				# insert a room between the current room and a number (mult) of subsequent rooms
				print('insert %s %d' % (room.name, mult))
				for i in range(mult):
					roomname = 'room %s' % alphaname(numrooms)
					node = DungeonNode(roomname)
					dests = [self.nodes[name] for name in room.next]
					self.node_insert(node, srcs=[room], dests=dests)
					numrooms += 1
					rooms.append(roomname)
			elif opt == 'connect':
				# connect this room back to a number (mult) of visited rooms
				print('connect %s %d' % (room.name, mult))
				samplelist = list(self.nodes.values())[:]
				for src in room.previous:
					samplelist.remove(self.nodes[src])
				prevrooms = sample(samplelist, min(mult, lenv))
				for p in prevrooms:
					p.next.insert(0, room.name)
					room.previous.append(p.name)

		self.set_end()

	def print(self):
		print()
		print('\tDungeon:')
		index = 1
		visited = []
		nodetags = ['room A']
		while (len(nodetags) > 0):
			nodetag = nodetags.pop(0)
			node = self.nodes[nodetag]
			printline = '\t%d. %s' % (index, nodetag)
			for nextnode in node.next:
				printline += ' -> %s\n\t\t' % nextnode
				if (nextnode not in nodetags and nextnode not in visited):
					nodetags.append(nextnode)
			print(printline)
			index += 1
			visited.append(nodetag)
		print()

def main():
	print('Starting dungeon gen. Enter \'q\' to quit.')
	dungeon = DungeonGraph()
	while(1):
		rin = input('>> ')

		# skip, loop, append, insert, connect
		weights = [40, 23, 12, 17, 8]

		collapse_percent = 0.2

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

		dungeon.generate(weights, collapse_percent)
		dungeon.print()
		dungeon.clear()



if __name__ == '__main__':
	main()