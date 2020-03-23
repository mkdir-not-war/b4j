from random import choice, random, randint, sample

MAX_ROOMS = 16
MIN_ROOMS = 4
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

	def node_collapse(self, node):
		assert(node.type == 'room')
		node.type = 'intersection'

	def set_bigkey(self):
		start = self.nodes['start']
		depthtracker = {}
		depthtracker['start'] = 0
		rooms = [start]
		nextrooms = start.next[:] + start.previous[:]
		nextrooms.remove('lock')
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
				for nextroom in room.previous:
					if nextroom not in depthtracker:
						nextrooms.append(nextroom)
		keyroom = choice(rooms)
		self.nodes[keyroom.name].tag = 'bigkey'
		print('%s set to key' % keyroom.name)

	def clear(self):
		self.nodes = {}

	def generate(self, weights, collapse_percent):
		start = DungeonNode('start')
		lock = DungeonNode('lock')
		lock.type = 'intersection'
		lock.tag = 'biglock'
		end = DungeonNode('end')

		self.node_append(start)
		self.node_append(lock, srcs=[start])
		self.node_append(end, srcs=[lock])

		# build rooms out
		options = ['skip', 'loop', 'append', 'connect']
		weights = weights
		visited = []
		rooms = ['start']
		numrooms = 0
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
				samplelist.remove("lock")
				samplelist.remove("end")
				for src in room.previous:
					samplelist.remove(src)
				for dest in room.next:
					samplelist.remove(dest)
				prevrooms = sample(samplelist, min(mult, len(samplelist)))
				for pname in prevrooms:
					p = self.nodes[pname]
					p.next.insert(0, room.name)
					room.previous.append(pname)

		self.set_bigkey()

	def print(self):
		print()
		print('\tDungeon:')
		index = 1
		visited = []
		nodenames = ['start']
		while (len(nodenames) > 0):
			nodename = nodenames.pop(0)
			node = self.nodes[nodename]
			if (node.tag != ''):
				nodename += ' (%s)' % node.tag
			printline = '\t%d. %s' % (index, nodename)
			for nextnode in node.next:
				nextnodename = nextnode
				if (self.nodes[nextnode].tag != ''):
					nextnodename += ' (%s)' % self.nodes[nextnode].tag
				printline += ' -> %s\n\t\t' % nextnodename
				if (nextnode not in nodenames and nextnode not in visited):
					nodenames.append(nextnode)
			print(printline)
			index += 1
			visited.append(nodename)

def main():
	print('Starting dungeon gen. Enter \'q\' to quit.')
	dungeon = DungeonGraph()
	while(1):
		rin = input('>> ')

		# skip, loop, append, connect
		#weights = [80, 23, 12, 20]
		weights = [80, 20, 10, 20]

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