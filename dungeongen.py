from random import choice, random

class DungeonNode:
	def __init__(self, tag='', nodetype=''):
		self.tag = tag
		self.type = nodetype
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
			node.previous.append(src.tag)
			src.next.append(node.tag)
		for dest in dests:
			node.next.append(dest)
			dest.previous.append(node.tag)
		self.nodes[node.tag] = node

	def node_insert(self, node, srcs=[], dests=[]):
		for src in srcs:
			for dest in dests:
				if (dest.tag in src.next):
					src.next.remove(dest.tag)
					dest.previous.remove(src.tag)
		node_append(node, srcs, dests)

	def node_collapse(self, node):
		assert(node.type not in ['key', 'lock', 'start', 'end'])
		node.type = 'intersection'

	def clear(self):
		self.nodes = {}

	def generate(self):
		start = DungeonNode('start')
		end = DungeonNode('end')

		self.node_append(start)
		self.node_append(end, srcs=[start])

	def print(self):
		print('Dungeon:')
		index = 1
		visited = []
		nodetags = ['start']
		while (len(nodetags) > 0):
			nodetag = nodetags.pop(0)
			node = self.nodes[nodetag]
			printline = '%d. %s' % (index, nodetag)
			for nextnode in node.next:
				printline += ' -> %s\n' % nextnode
				if (nextnode not in nodetags and nextnode not in visited):
					nodetags.append(nextnode)
			print(printline)
			index += 1
			visited.append(nodetag)
		print('~' * 50)

def main():
	print('Starting dungeon gen. Enter \'q\' to quit.')
	dungeon = DungeonGraph()
	while(1):
		rin = input('>> ')
		if (rin == 'q'):
			return
		dungeon.generate()
		dungeon.print()
		dungeon.clear()



if __name__ == '__main__':
	main()