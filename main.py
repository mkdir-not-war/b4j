import pygame
from math import sqrt
from random import choice, random

def dot(v1, v2):
	result = v1[0]*v2[0] + v1[1]*v2[1]
	return result

def v2_add(v1, v2):
	result = (v1[0]+v2[0], v1[1]+v2[1])
	return result

def length(v):
	result = sqrt(v[0]**2 + v[1]**2)
	return result

def normalize(v):
	vlen = length(v)
	result = (v[0]/vlen, v[1]/vlen)
	return result

def arrayget(array, width, p):
	x, y = p
	result = array[y*width + x]
	return result

def arrayset(array, width, p, val):
	x, y = p
	array[y*width + x] = val

def insertnode(node, val, list):
	index = -1
	i = 0
	while i < len(list) and index < 0:
		if val <= list[i][1]:
			break
		else:
			i += 1
	index = i
	list.insert(index, (node, val))

def grid_print(grid, dimensions, func):
	width, height = dimensions
	for j in range(height):
		print(''.join([func(x) for x in grid[(width*j):(width*(j+1))]]))
	print()

# define floodfill arrays out of scope in C# so it doesn't call GC a ton
def floodfill(geomap, *pos, dist=None):
	height, width = geomap.height, geomap.width
	colormap = [False] * (height*width) # size of map
	for p in pos:
		arrayset(colormap, width, p, True)
	border = [] # size of (height+width)*2
	for p in pos:
		border.append((p, 0))
	result = [] # size of (width*height)
	result.extend(pos)

	while (len(border) > 0 and (dist==None or border[0][1] <= dist)):
		r, rdist = border.pop(0)
		rx, ry = r
		for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
				v = (rx+dx, ry+dy)
				
				if (not geomap_iscollision(geomap, v) and \
					not arrayget(colormap, width, v)):

					arrayset(colormap, width, v, True)
					if (rdist+1 <= dist):
							result.append(v)
					insertnode(v, rdist+1, border)

	return result

def sign(n):
	if (n < 0):
		return -1
	elif (n > 0):
		return 1
	else:
		return 0

def bresenham_v(src, dest, result):
	x = src[0]
	for y in range(src[1], dest[1]+1):
		result.append((x, y))

def bresenham_h(src, dest, result):
	y = src[1]
	for x in range(src[0], dest[0]+1):
		result.append((x, y))

def bresenham(src, dest):
	result = []

	dx = dest[0] - src[0]
	dy = dest[1] - src[1]

	if dy == 0:
		if (dx > 0):
			bresenham_h(src, dest, result)
			return result
		else:
			bresenham_h(dest, src, result)
			return result[::-1]
		
	elif dx == 0:
		if (dy > 0):
			bresenham_v(src, dest, result)
			return result
		else:
			bresenham_v(dest, src, result)
			return result[::-1]

	err = 0.0

	# if diff in x is larger, increment in x. If delta-x is small but y is big, increment y
	if (dx**2 > dy**2):
		derr = abs(dy / dx)
		if (dx > 0):
			y = src[1]
			for x in range(src[0], dest[0]):
				result.append((x, int(y)))
				err += derr
				if err >= 0.5:
					y += sign(dy)
					err -= 1.0
			result.append(dest)
		else:
			y = dest[1]
			for x in range(dest[0], src[0]):
				result.insert(0, (x, int(y)))
				err += derr
				if err >= 0.5:
					y -= sign(dy)
					err -= 1.0
			result.insert(0, src)
	else:
		derr = abs(dx / dy)
		if (dy > 0):
			x = src[0]
			for y in range(src[1], dest[1]):
				result.append((x, int(y)))
				err += derr
				if err >= 0.5:
					x += sign(dx)
					err -= 1.0
			result.append(dest)
		else:
			x = dest[0]
			for y in range(dest[1], src[1]):
				result.insert(0, (x, int(y)))
				err += derr
				if err >= 0.5:
					x -= sign(dx)
					err -= 1.0
			result.insert(0, src)
	
	return result

def get_tile_raycast(geomap, pos, direction, maxdist=100):
	dest = (int(pos[0]+0.5+direction[0]*maxdist), int(pos[1]+0.5+direction[1]*maxdist))
	points2check = bresenham(pos, dest)
	index = 1
	for i in range(len(points2check)):
		if (not geomap_iscollision(geomap, points2check[i])):
			index = i
		else:
			break

	return points2check[:index+1]


def get_area_in_direction(geomap, direction, *pos, dist=1):
	height, width = geomap.height, geomap.width
	
	colormap = [False] * (height*width) # size of map
	result = []

	for p in pos:
		raycastlist = get_tile_raycast(geomap, p, direction, maxdist=dist)
		for newtile in raycastlist:
			if (not arrayget(colormap, width, newtile)):
				arrayset(colormap, width, newtile, True)
				result.append(newtile)

	return result

# assumes u = (1, 0)
def get_rotated_vecs(v, vecs):
	u = (1, 0)
	cos = v[0]/length(v)
	sin = sqrt(1.0 - cos**2)
	if (v[1] < 0):
		sin *= -1
	result = []
	for vec in vecs:
		x2 = vec[0]*cos - vec[1]*sin
		y2 = vec[0]*sin + vec[1]*cos
		result.append((x2, y2))
	return result

def distance_less_than(p1, p2, dist):
	result = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 < dist**2)
	return result

def poly_contains(polygon, x, y):
	numverts = len(polygon)
	intersections = 0
	for i in range(numverts):
		x1 = polygon[i][0]
		y1 = polygon[i][1]
		x2 = polygon[(i+1)%numverts][0];
		y2 = polygon[(i+1)%numverts][1];

		if (((y1 <= y and y < y2) or
			(y2 <= y and y < y1)) and
			x < ((x2 - x1) / (y2 - y1) * (y - y1) + x1)):
			intersections += 1
	return (intersections & 1) == 1 

def poly_collides(poly1, poly2):
	for (x, y) in poly1:
		if (poly_contains(poly2, x, y)):
			return True
	for (x, y) in poly2:
		if (poly_contains(poly1, x, y)):
			return True
	return False

def get_screen_coord(playerpos, playeroff, worldp):
	diffx = worldp[0]-playerpos[0]
	diffy = worldp[1]-playerpos[1]
	return(playeroff[0]+diffx, playeroff[1]+diffy)

BADDY_HITBOX_SCALE = 0.8

class Entity:
	def __init__(self, pos, width=1, direction=(0,1), enemytype=None):
		self.p = pos[:]
		self.dp = [0, 0]
		self.direction = direction[:]
		self.width = width
		self.centeroffset = width * tilewidth/2

		self.stuntimer = 0

		self.hitbox = None
		self.brain = None
		self.enemytype = enemytype

		self.DESTROY = False

		self.hp = 1
		self.weight = 2
		self.poise = 0

		if (enemytype != None):
			# stats
			self.hp = enemytype.maxhp
			self.weight = enemytype.weight
			self.poise = enemytype.poise

			# build the hitbox as a list of offsets from the top left corner of the sprite
			self.width = enemytype.width
			self.centeroffset = tilewidth * self.width/2
			offset = BADDY_HITBOX_SCALE * tilewidth * self.width/2
			self.hitbox = [
				(self.centeroffset-offset, self.centeroffset-offset), 
				(self.centeroffset-offset, self.centeroffset+offset),
				(self.centeroffset+offset, self.centeroffset+offset),
				(self.centeroffset+offset, self.centeroffset-offset)]

WEIGHT_FRAME_MULT = 10

def entity_getcenter(entity):
	result = (entity.p[0]+entity.centeroffset, entity.p[1]+entity.centeroffset)
	return result

def entity_hurt(entity, hurtbox, megabrain):
	entity.hp -= 1
	if (entity.hp <= 0):
		entity.DESTROY = True
		if (entity.brain != None):
			megabrain_removebrain(megabrain, entity.brain)

	direction = hurtbox.direction
	if (hurtbox.attack.force > entity.poise):
		entity.stuntimer = entity.weight * WEIGHT_FRAME_MULT
		entity.dp = direction[:]
		if (entity.brain != None and entity.brain.currentbehavior == 'attack'):
			entity.brain.attackstate = None
			entity.brain.currentattack = None
			entity.brain.currentbehavior = 'threaten'
			entity.brain.actionframe = entity.enemytype.timebetweenattacks
			megabrain.currentattacking -= 1

def entity_get_hitbox(entity):
	return [(x+entity.p[0], y+entity.p[1]) for (x, y) in entity.hitbox]

'''
def entity_update_brain(entity):
	if (entity.brain != None):
		brain_update(entity.brain)
'''

def entity_update_physics(entity):
	# decrement stun timer if needed
	if (entity.stuntimer > 0):
		entity.stuntimer -= 1

	speed = 0
	# move facing direction to movetarget, set speed if far enough away
	if (entity.enemytype != None and entity.brain != None):
		movetarget = entity.brain.movetarget
		if (movetarget != None):
			center = entity_getcenter(entity)
			entity.direction = normalize((
				movetarget[0]-center[0], 
				movetarget[1]-center[1]))	
			if distance_less_than(center, movetarget, tilewidth):
				speed = entity.enemytype.speed

	# if not stunned, delta-position is set to direction
	if (entity.stuntimer <= 0):
		entity.dp[0] = entity.direction[0]
		entity.dp[1] = entity.direction[1]

	# if this entity is the type that moves at all, move in delta-position
	# >> entities with speed=0 won't move back when stunned <<
	if (speed > 0):
		new_p = (
			entity.p[0] + entity.dp[0] * speed,
			entity.p[1] + entity.dp[1] * speed)
		entity.p = new_p

	# refresh velocity vector
	entity.dp = [0, 0]

class EnemyType:
	def __init__(
		self, dr, ib, t2f, 
		widthintiles=1, maxhp=1, poise=0, weight=1, speed=0, timebetweenattacks=60, attacks=[]):

		self.attacks = attacks
		self.timebetweenattacks = timebetweenattacks
		# attack objects, hp and range at which to use them
		self.detectionradius = dr # read by megabrain
		self.initialbehavior = ib # read by megabrain
		self.time2forget = int(t2f*30) # time in seconds that this enemy will search for player
		self.speed = speed
		self.width = widthintiles
		self.maxhp = maxhp
		self.poise = poise # use to determine if stunned or not from attack
		self.weight = weight # use to determine how long stunned

enemytypes = {}
enemytypes['small melee creature'] = EnemyType(
	5, 'idle', 2, 
	widthintiles=1, maxhp=3, speed=0,
	attacks=['jab', 'uppercut'])
enemytypes['small ranged creature'] = EnemyType(
	5, 'lookout', 20, 
	widthintiles=1, maxhp=3, speed=0,
	attacks=['jab_ranged'])
enemytypes['medium melee creature'] = EnemyType(
	5, 'lookout', 20, 
	widthintiles=2, maxhp=3, speed=0,
	attacks=['jab', 'uppercut'])
enemytypes['large melee creature'] = EnemyType(
	5, 'lookout', 20, 
	widthintiles=3, maxhp=3, speed=0,
	attacks=['jab', 'uppercut'])

# megabrain handles coordination between multiple hostile enemy AIs
class MegaBrain:
	def __init__(self):
		self.maxtime = 10
		self.timer = self.maxtime
		self.maxattacking = 3
		self.currentattacking = 0
		self.brains = []

def brain_updatetimer(brain):
	brain.timer -= 1
	if (brain.timer <= 0):
		brain.timer = brain.maxtime

def megabrain_addbrain(megabrain, brain):
	megabrain.brains.append(brain)

def megabrain_removebrain(megabrain, brain):
	megabrain.brains.remove(brain)

stufftodraw = [] ############################################### debug art #######################

def megabrain_update(megabrain, geomap, hurtboxes, player, screen):
	global stufftodraw
	stufftodraw.clear()

	# check stuff and set new behaviors if needed on the brains
	for b in megabrain.brains:
		e = b.entity

		# check if player is in detection range
		player_detected = False
		player_tile = get_tile_pos(player.p)

		e_tiles = []
		topleftpos = v2_add(e.hitbox[0], e.p)
		for i in range(e.width+1):
			for j in range(e.width+1):
				offset = (i*tilewidth*BADDY_HITBOX_SCALE, j*tilewidth*BADDY_HITBOX_SCALE)
				tilepos = get_tile_pos(v2_add(topleftpos, offset))
				e_tiles.append(tilepos)

		if (player_tile in e_tiles):
			player_detected = True
		else:
			detection_tiles = get_area_in_direction(
				geomap, 
				e.direction,
				*e_tiles,
				dist = e.enemytype.detectionradius)
			if (player_tile in detection_tiles):
				player_detected = True
			#####################################
			for t in detection_tiles:
				i, j = get_world_pos(t)
				newtile = [(i, j), 
					(i+tilewidth, j), 
					(i+tilewidth, j+tilewidth), 
					(i, j+tilewidth)]
				stufftodraw.append(newtile)
			#####################################


		if b.currentbehavior == 'idle':
			brain_idle_update(b, geomap, player_detected)
		elif b.currentbehavior == 'lookout':
			brain_lookout_update(b, geomap, player_detected)
		elif b.currentbehavior == 'threaten':
			brain_threaten_update(b, geomap, player, megabrain, player_detected)
		elif b.currentbehavior == 'attack':
			brain_attack_update(b, geomap, player, megabrain, hurtboxes)

	# pick attackers
	if (megabrain.currentattacking < megabrain.maxattacking):
		# shuffle the brains, maybe divide spacially so that more likely to have attacks from
		# mutliple directions instead of only just one direction?? Need to test for feel.
		for b in megabrain.brains:
			if (b.currentbehavior == 'threaten' and b.actionframe <= 0):
				continue ################################# SKIP ATTACKING DEBUG #############
				if (len(b.attacksinrange) > 0):
					b.currentattack = b.attacksinrange[0] # use choice
					b.currentbehavior = 'attack'
					b.attackstate = 'startup'
					b.actionframe = b.currentattack.startup
					megabrain.currentattacking += 1
					if (megabrain.currentattacking >= megabrain.maxattacking):
						break
				
	brain_updatetimer(megabrain)

class Brain:
	def __init__(self, entity):
		self.entity = entity
		self.attacks = []
		self.attacksinrange = [] # maybe just a bool array referencing attacks? Can be optimized

		self.currentattack = None # set by megabrain
		self.attackstate = None
		self.actionframe = 0

		self.movetarget = None # set by megabrain
		self.currentbehavior = 'lookout'
		self.timesincedetection = 0
		self.time2turn = 0

		if (entity.enemytype != None):
			self.currentbehavior = entity.enemytype.initialbehavior

IDLE_TURN_MIN_TIME = 25
IDLE_TURN_MAX_TIME = 80

# use idle for bosses or enemies who need to watch an entrance, otherwise default to lookout
def brain_idle_update(b, geomap, player_detected):
	if (player_detected):
		b.currentbehavior = 'threaten'
		b.actionframe = b.entity.enemytype.timebetweenattacks

def brain_lookout_update(b, geomap, player_detected):
	if (b.actionframe == 0):
		b.time2turn = int(
			random() * (IDLE_TURN_MAX_TIME - IDLE_TURN_MIN_TIME) + IDLE_TURN_MIN_TIME)
	b.actionframe += 1

	if (player_detected):
		b.currentbehavior = 'threaten'
		b.actionframe = b.entity.enemytype.timebetweenattacks
	elif (b.actionframe >= b.time2turn):
		b.actionframe = 0
		newdir = choice(carddirs)
		b.entity.direction = newdir

def brain_threaten_update(b, geomap, player, mb, player_detected):
	if mb.timer == 1:
		# update path finding, set b.movetarget
		b.movetarget = player.p

	# update action timer
	if (b.actionframe > 0):
		b.actionframe -= 1

	# build in-range attacks list/bool array??
	b.attacksinrange.clear()
	if (player_detected):
		b.timesincedetection = 0
		for atk in b.attacks:
			if (distance_less_than(player.p, b.entity.p, atk.range)):
				b.attacksinrange.append(atk)
	else:
		b.timesincedetection += 1
		if (b.timesincedetection > b.entity.enemytype.time2forget):
			b.currentbehavior = 'lookout'
			b.movetarget = None
			b.actionframe = 0

def brain_attack_update(b, geomap, player, mb, hurtboxes):
	# assume entity has enemytype
	assert(b.entity.enemytype != None)

	if (b.actionframe > 0):
		b.actionframe -= 1
	if (b.actionframe <= 0):
		e = b.entity
		atk = b.currentattack
		# if done attacking, change behavior to threaten and reduce mb.currentattacking by 1
		continueprocessing = True
		while (continueprocessing):
			if b.attackstate == 'startup':
				b.attackstate = 'active'
				b.actionframe = atk.activeframes
				hurtbox = [p for p in atk.box]
				hurtboxes.append(hurtbox_get(
					hurtbox, 
					e.direction, 
					entity_getcenter(e), 
					atk))
			elif b.attackstate == 'active':
				b.attackstate = 'cooldown'
				b.actionframe = atk.cooldown
			elif b.attackstate == 'cooldown':
				if (not atk.nextatk == None):
					b.attackstate = 'startup'
					b.currentattack = atk.nextatk
					b.actionframe = atk.nextatk.startup
				else:
					b.attackstate = None
					b.currentattack = None
					b.currentbehavior = 'threaten'
					b.actionframe = b.entity.enemytype.timebetweenattacks
					mb.currentattacking -= 1

			# use this for chaining attacks (e.g. jab -> projectile)
			if (b.actionframe > 0 or b.attackstate == None):
				continueprocessing = False

class Hurtbox:
	def __init__(self, box, direction, attack):
		self.attack = attack
		self.box = box[:]
		self.framesleft = attack.hurtframes
		self.direction = direction
		self.speed = attack.speed
		self.destroy = False

def hurtbox_get(box, direction, position, attack):
	hb = get_rotated_vecs(direction, box)
	hb = [(x+position[0], y+position[1]) for (x, y) in hb]
	return Hurtbox(hb, direction, attack)

def hurtbox_update(hurtbox, geomap):
	# fixed time step, no need for delta time
	vx = hurtbox.direction[0] * hurtbox.speed
	vy = hurtbox.direction[1] * hurtbox.speed
	if (hurtbox.speed > 0):
		new_box = [(x+vx, y+vy) for (x, y) in hurtbox.box]

		geometry = geomap_gettilegeo_frombox(geomap, new_box)

		for g in geometry:
			if (poly_collides(g, new_box)):
				# destroy projectiles when they hit geometry
				hurtbox.destroy = True

		hurtbox.box = new_box

	hurtbox.framesleft -= 1

class NoneAction:
	def __init__(self):
		self.actiontype = 'none'

noneaction = NoneAction()

class Dash:
	def __init__(self):
		self.actiontype = 'dash'
		self.speed = 12

		self.activeframes = 10
		self.chainframes = 5 # how many frames of beginning of cooldown a chain can start
		self.cooldown = 12

dashaction = Dash()

class Player:
	def __init__(self):
		self.state = 'idle'
		self.dir = [0, 0]
		self.p = [0, 0]
		self.dp = [0, 0]
		self.ddp = [0, 0]
		self.size = 1
		self.movebox = []

		self.actionframe = 0
		self.currentaction = noneaction

		self.maxhp = 5
		self.hp = self.maxhp

		self.maxstam = 5
		self.stam = self.maxstam

		self.jab = None
		self.uppercut = None
		self.jab_projectile = None
		self.jab_upgraded = None

def player_update(player, hurtboxes):
	if (player.actionframe > 0):
		player.actionframe -= 1
	if (player.actionframe <= 0):
		if player.currentaction.actiontype == 'dash':
			if player.state == 'active':
				player.state = 'chainable'
				player.actionframe = dashaction.chainframes
			elif player.state == 'chainable':
				player.state = 'cooldown'
				player.actionframe = dashaction.cooldown
			elif player.state == 'cooldown':
				player.state = 'idle'
				player.currentaction = noneaction

		elif player.currentaction.actiontype == 'attack':
			continueprocessing = True
			while (continueprocessing):
				if player.state == 'startup':
					player.state = 'active'
					player.actionframe = player.currentaction.activeframes
					hurtbox = [p for p in player.currentaction.box]
					hurtboxes.append(hurtbox_get(
						hurtbox, 
						player.dir, 
						player.p, 
						player.currentaction))
				elif player.state == 'active':
					player.state = 'cooldown'
					player.actionframe = player.currentaction.cooldown
				elif player.state == 'cooldown':
					if (not player.currentaction.nextatk == None):
						player_attack(player, player.currentaction.nextatk)
					else:
						player.state = 'idle'
						player.currentaction = noneaction

				# use this for chaining attacks (e.g. jab -> projectile)
				if (player.actionframe > 0 or player.state == 'idle'):
					continueprocessing = False
				

def player_attack(player, attack):
	player.state = 'startup'
	player.currentaction = attack
	player.actionframe = attack.startup

def player_hurt(player, attack):
	player.hp -= 1
	if player.hp <= 0:
		pass
		# dead
	# set effects like burning etc.
	# push back??

def player_dash(player):
	if (player.state == 'idle' or 
		(player.currentaction.actiontype == 'dash' and player.state == 'chainable')):
		player.state = 'active'
		player.currentaction = dashaction
		player.actionframe = dashaction.activeframes


class Attack:
	def __init__(self, startup, activeframes, cooldown, box, 
		force=1, rangeofatk=0, hurtframes=0, speed=0, nextatk=None):

		self.actiontype = 'attack'
		self.startup = startup # frames int
		self.activeframes = activeframes # frames before entering cooldown
		self.cooldown = cooldown # frames int
		self.box = box # use hurtbox_get to create object
		self.speed = speed # for moving hit boxes
		self.nextatk = nextatk # auto-start this next if not None

		self.range = rangeofatk
		self.force = force

		self.hurtframes = hurtframes # frames the hurtbox exists, default to activeframes
		if (hurtframes == 0):
			self.hurtframes = activeframes

attacktypes = {}
attacktypes['jab'] = Attack(
	1, 4, 20, 
	[(22, 12), (48, 12), (48, -12), (22, -12)],
	rangeofatk=80)
attacktypes['uppercut'] = Attack(
	24, 6, 36,
	[(22, 12), (48, 12), (48, -12), (22, -12)],
	rangeofatk=80)
attacktypes['jab_ranged'] = Attack(
	1, 4, 20,
	[(22, 12), (48, 12), (48, -12), (22, -12)],
	rangeofatk=200, hurtframes=30, speed=8)

class GeoMap:
	def __init__(self, dimensions, geo):
		self.width, self.height = dimensions
		self.geo = geo # bool map of collidable geometry, width 1
		self.costmap = geomap_getpathingmap(self)

def geomap_iscollision(geomap, pos):
	result = geomap.geo[geomap.width * pos[1] + pos[0]]
	return result

def geomap_getadjacent(geolist, width, height, pos, diagonal=False):
	result = {}
	for j in range(-1, 2):
		for i in range(-1, 2):
			if (i == 0 and j == 0):
				continue
			if (diagonal or (i+j != 1 and i+j != -1)):
				adjpos = (pos[0]+i, pos[1]+j)

				if (adjpos[0] >= 0 and 
					adjpos[0] < width and
					adjpos[1] >= 0 and
					adjpos[1] < height):

					result[adjpos] = geolist[width * adjpos[1] + adjpos[0]]
	return result

# NOTE: assumes tile-position of entity is top-left corner.
def geomap_getwidemap(geomap, minpassagewidth):
	width, height = geomap.width, geomap.height
	prevgen = geomap.geo[:]

	# fill in passages off the map
	for j in range(height):
		for i in range(width):
			if (i == 0 or j == 0 or
				i == width-1 or j == height-1):
				prevgen[width * j + i] = True

	newgeo = prevgen[:]

	for gen in range(minpassagewidth-1):
		# grow on the left and top side of walls
		for j in range(1, height-1):
			for i in range(1, width-1):
				if (prevgen[width * j + i] == False):
					# left side
					if (prevgen[width * j + (i+1)]):
						newgeo[width * j + i] = True
					# top side
					if (prevgen[width * (j+1) + i]):
						for k in range(minpassagewidth):
							newgeo[width * j + (i-k)] = True
		prevgen = newgeo[:]

	# DEBUG ###########
	
	def func(x):
		return '# ' if x else '. '
	print('~~ geomap with minimum passage width: %d ' % minpassagewidth + '~'*20)
	print()
	grid_print(geomap.geo, (width, height), func)
	grid_print(newgeo, (width, height), func)
	print('~'*60)
	print()
	
	###################

	result = GeoMap((width, height), newgeo)
	return result

# DIRECTION STUFF FOR PATHFINDING ########################
N = (0, -1)
S = (0, 1)
E = (1, 0)
W = (-1, 0)
NE = (1, -1)
NW = (-1, -1)
SE = (1, 1)
SW = (-1, 1)

carddirs = [N, S, E, W]

oppcornerdict = {}
oppcornerdict[N] = [SE, SW]
oppcornerdict[S] = [NE, NW]
oppcornerdict[E] = [NW, SW]
oppcornerdict[W] = [SE, NE]

neighedgedict = {}
neighedgedict[NE] = [N, E]
neighedgedict[NW] = [N, W]
neighedgedict[SE] = [S, E]
neighedgedict[SW] = [S, W]
#########################################################

# NOTE: pathing maps works best with structures (contiguous walls) that DON'T intersect the perimeter
def geomap_getpathingmap(geomap):
	width, height = geomap.width, geomap.height
	gens = 12

	pathcost = 1
	nonwallcost = 3#10
	wallcost = width*height

	prevgen = []
	for j in range(height):
		for i in range(width):
			if (i == 0 or j == 0 or
				i == width-1 or j == height-1):
				prevgen.append(wallcost)
			elif (geomap.geo[width * j + i] == True):
				prevgen.append(wallcost)
			else:
				prevgen.append(pathcost)

	result = prevgen[:]

	# don't include passages off the map (wouldn't make a difference though)
	for gen in range(gens):
		for j in range(1, height-1):
			for i in range(1, width-1):
				# look at non-wall spots
				if (prevgen[width * j + i] == pathcost):
					adjposdict = geomap_getadjacent(prevgen, width, height, (i, j), diagonal=True)

					cardwalls = [
						adjposdict[v2_add((i, j), d)] for d in carddirs \
						if adjposdict[v2_add((i, j), d)] > pathcost
						]

					if (len(cardwalls) >= 3):
						result[width * j + i] = nonwallcost
					else:
						for d in carddirs:
							# edge neighbor is a wall
							if (adjposdict[v2_add((i, j), d)] > pathcost):
								# grab opposite corners and neighbor edges
								oppcorners = oppcornerdict[d]
								neighedges = []
								if (neighedgedict[oppcorners[0]][0] == neighedgedict[oppcorners[1]][0]):
									# north or south matches (first index), keep east and west
									neighedges.append((oppcorners[0],
										neighedgedict[oppcorners[0]][1]))
									neighedges.append((oppcorners[1],
										neighedgedict[oppcorners[1]][1]))
								elif (neighedgedict[oppcorners[0]][1] == neighedgedict[oppcorners[1]][1]):
									# east or west matches (second index), keep north and south
									neighedges.append((oppcorners[0],
										neighedgedict[oppcorners[0]][0]))
									neighedges.append((oppcorners[1],
										neighedgedict[oppcorners[1]][0]))

								# if first opposite corner is a wall
								if (adjposdict[v2_add((i, j), neighedges[0][0])] > pathcost):
									# and the corresponding neighbor edge is also a wall
									if (adjposdict[v2_add((i, j), neighedges[0][1])] > pathcost):
										# if the other opp corner exists, but no edge, then skip
										if (adjposdict[v2_add((i, j), neighedges[1][0])] > pathcost and
											adjposdict[v2_add((i, j), neighedges[1][1])] == pathcost):
											pass
										else:
											result[width * j + i] = nonwallcost
											break
								# if second opposite corner is a wall
								elif (adjposdict[v2_add((i, j), neighedges[1][0])] > pathcost):
									# and the corresponding neighbor edge is also a wall
									if (adjposdict[v2_add((i, j), neighedges[1][1])] > pathcost):
										# if the other opp corner exists, but no edge, then skip
										if (adjposdict[v2_add((i, j), neighedges[0][0])] > pathcost and
											adjposdict[v2_add((i, j), neighedges[0][1])] == pathcost):
											pass
										else:
											result[width * j + i] = nonwallcost
											break

		prevgen = result[:]		

	# DEBUG ###########
	
	def func(x):
		return '# ' if x else '. '
	def func2(x):
		return '. ' if x==1 else 'x ' if x<100 else '# '
	grid_print(geomap.geo, (width, height), func)
	grid_print(result, (width, height), func2)
	
	###################

	return result

def geomap_astar(geomap, pos, target):
	# only use cardinal directions (carddirs)
	pass

# position is center of object, dimensions is (width, height)
def geomap_gettilegeo_frompos(geomap, position, dimensions):
	px, py = position
	w, h = dimensions

	minx, miny = get_tile_pos((px-w/2, py-h/2))
	maxx, maxy = get_tile_pos((px+w/2, py+h/2))

	result = []
	for i in range(minx, maxx+1):
		for j in range(miny, maxy+1):
			if (geomap_iscollision(geomap, (i, j))):
				newtile = [(i*tilewidth, j*tilewidth), 
					((i+1)*tilewidth, j*tilewidth), 
					((i+1)*tilewidth, (j+1)*tilewidth), 
					(i*tilewidth, (j+1)*tilewidth)]
				result.append(newtile)
	return result

def geomap_gettilegeo_frombox(geomap, box):
	result = []
	for point in box:
		i, j = get_tile_pos(point)
		if (geomap_iscollision(geomap, (i, j))):
			newtile = [(i*tilewidth, j*tilewidth), 
				((i+1)*tilewidth, j*tilewidth), 
				((i+1)*tilewidth, (j+1)*tilewidth), 
				(i*tilewidth, (j+1)*tilewidth)]
			result.append(newtile)
	return result


tilewidth = 50

def get_tile_pos(worldpos):
	wx, wy = worldpos
	tx = int(wx // tilewidth)
	if (wx < 0):
		tx -= 1
	ty = int(wy // tilewidth)
	if (ty < 0):
		ty -= 1
	result = (tx, ty)
	return result

def get_world_pos(tilepos, offset=(0, 0)):
	tx, ty = tilepos
	ox, oy = offset
	result = ((tx+ox)*tilewidth, (ty+oy)*tilewidth)
	return result

class ReadEntity:
	def __init__(self, tile, etype):
		self.tile = tile
		self.etype = etype

def spawnentities(readentities, megabrain):
	entities = []

	for re in readentities:
		enemytype = None
		
		if (re.etype in enemytypes):
			enemytype = enemytypes[re.etype]

		worldpos = get_world_pos(re.tile)
		
		newent = Entity(worldpos, enemytype=enemytype)
		newent.brain = Brain(newent)
		for atkname in attacktypes:
			newent.brain.attacks.append(attacktypes[atkname])
		entities.append(newent)

	for e in entities:
		megabrain_addbrain(megabrain, e.brain)

	return entities

def tilemap_load(filepath):
	geometry = []
	width = 0
	height = 0
	spawn = None
	readentities = []

	readstate = 'layout'
	entitiesdict = {}

	f = open(filepath, 'r')
	for line in f:
		sline = line.strip('\n')

		# check for tags
		if (sline == 'end-layout'):
			readstate = 'entities'
			continue
		elif (sline == 'end-entities'):
			break

		# read map layout
		if (readstate == 'layout'):
			width = len(sline)
			for index in range(len(sline)):
				char = sline[index]
				# geometry
				if (char == '#'):
					geometry.append(True)
				else:
					geometry.append(False)
				# spawn location
				if (char == 's'):
					spawn = (index, height)
				# entities
				if (char != 's' and char != '#' and char != '.'):
					entitiesdict[char] = (index, height)
			height += 1
		# read entities on map
		elif (readstate == 'entities'):
			# put entity object into the dictionary
			spline = sline.split(':')
			assert(spline[0] in entitiesdict)
			readentities.append(ReadEntity(entitiesdict[spline[0]], spline[1]))

	f.close()

	def func(x):
		return '# ' if x else '. '
	#grid_print(geometry, (width, height), func)

	return (width, height), geometry, spawn, readentities

def main():
	pygame.init()

	grey = pygame.Color(200, 200, 200)
	lightgrey = pygame.Color(125, 125, 125)
	darkred = pygame.Color(80, 0, 0)
	lightred = pygame.Color(250, 100, 100)
	red = pygame.Color('red')
	black = pygame.Color('black')

	# Set the width and height of the screen (width, height).
	screendim = (1050, 750)
	midscreen = (screendim[0]//2, screendim[1]//2)
	screen = pygame.display.set_mode(screendim)
	pygame.display.set_caption("B4J prototype")

	done = False
	clock = pygame.time.Clock()
	FPS = 30

	# input stuff
	pygame.joystick.init()

	# start loading the map and the stuff in it
	entities = []
	hurtboxes = []
	dimensions, tilemap, spawnloc, readentities = tilemap_load('./bigmap.txt')

	geomap = GeoMap(dimensions, tilemap)
	geomap_2wide = geomap_getwidemap(geomap, 2)
	#geomap_3wide = geomap_getwidemap(geomap, 3)

	# start up mega brain
	megabrain = MegaBrain()

	# spawn baddies, doors, etc
	entities = spawnentities(readentities, megabrain)

	# player stuff
	playeroffset = midscreen
	player = Player()
	player.p = get_world_pos(spawnloc, (0.5, 0.5))
	speed = 3.7
	player.dir = (0, 1)
	player.movebox = [(18, 0), (0, -18), (-18, 0), (0, 18)] 

	player.jab = attacktypes['jab']
	player.uppercut = attacktypes['uppercut']
	player.jab_upgraded = attacktypes['jab_ranged']


	prev_input = []
	curr_input = [] # int list

	while not done:
		clock.tick(FPS)

		# poll input
		prev_input = curr_input[:]
		for event in pygame.event.get(): # User did something.
			if event.type == pygame.QUIT: # If user clicked close.
				done = True # Flag that we are done so we exit this loop.
			elif event.type == pygame.JOYBUTTONDOWN:
				print("Joystick button pressed.")

			elif event.type == pygame.KEYDOWN:
				curr_input.append(event.key)
			elif event.type == pygame.KEYUP:
				if event.key in curr_input:
					curr_input.remove(event.key)

		# keypad handle input
		moveinput_dir = [0, 0]
		if pygame.K_ESCAPE in curr_input:
			done = True
		if player.state == 'idle':
			if pygame.K_SPACE in curr_input:
				pass

			if pygame.K_UP in curr_input:
				moveinput_dir[1] += -1
			if pygame.K_DOWN in curr_input:
				moveinput_dir[1] += 1
			if pygame.K_LEFT in curr_input:
				moveinput_dir[0] += -1
			if pygame.K_RIGHT in curr_input:
				moveinput_dir[0] += 1
			# face direction of movement whether colliding or not
			if (moveinput_dir[0] != 0 or moveinput_dir[1] != 0):
				movelen = length(moveinput_dir)
				player.dir = (moveinput_dir[0]/movelen, moveinput_dir[1]/movelen)

			if pygame.K_RCTRL in curr_input:
				player_dash(player)

			if pygame.K_KP0 in curr_input and not pygame.K_KP0 in prev_input:
				player_attack(player, player.jab_upgraded) #player.jab)
			elif pygame.K_KP1 in curr_input and not pygame.K_KP1 in prev_input:
				player_attack(player, player.uppercut)

		elif player.currentaction.actiontype == 'dash':
			if pygame.K_UP in curr_input:
				moveinput_dir[1] += -1
			if pygame.K_DOWN in curr_input:
				moveinput_dir[1] += 1
			if pygame.K_LEFT in curr_input:
				moveinput_dir[0] += -1
			if pygame.K_RIGHT in curr_input:
				moveinput_dir[0] += 1
			# face direction of movement whether colliding or not
			if (moveinput_dir[0] != 0 or moveinput_dir[1] != 0):
				movelen = length(moveinput_dir)
				if (player.state != 'active'):
					player.dir = (moveinput_dir[0]/movelen, moveinput_dir[1]/movelen)

			if pygame.K_RCTRL in curr_input and not pygame.K_RCTRL in prev_input:
				player_dash(player)

		elif player.currentaction.actiontype == 'blocking':
			if ((pygame.K_KP0 in curr_input and not pygame.K_KP0 in prev_input) or
				(pygame.K_KP1 in curr_input and not pygame.K_KP1 in prev_input)):
				pass # attempt to parry

		# movement calculation -> collision check -> update position
		if (not player.currentaction.actiontype == 'block'):
			# skip accel/friction for now
			direction = moveinput_dir[:]
			curr_speed = speed
			if (player.currentaction.actiontype == 'dash'):
				direction = player.dir[:]
				if (player.state == 'active'):
					curr_speed = dashaction.speed
				else:
					curr_speed = 0
			new_dp = [direction[0]*curr_speed, direction[1]*curr_speed] # use vec2 struct
			new_p = [new_dp[0] + player.p[0], new_dp[1] + player.p[1]] # use vec2 struct

			# check collision with new_p on geometry, entities and hurtboxes
			colliding = False

			# move these arrays out of the loop and just clear them here
			collisionboxes = []
			collisionentities = []
			collisionhbs = []

			new_p_box = []
			for (sx, sy) in player.movebox:
				vx = sx + new_p[0]
				vy = sy + new_p[1]
				new_p_box.append((vx, vy))

			geometry = geomap_gettilegeo_frompos(geomap, new_p, (36, 36))

			for p in geometry:
				if (poly_collides(p, new_p_box)):
					colliding = True
					collisionboxes.append(p)

			for e in entities:
				ehb = entity_get_hitbox(e)
				if (poly_collides(ehb, new_p_box)):
					colliding = True
					collisionboxes.append(ehb)
					collisionentities.append(e)

			if (not (player.currentaction.actiontype == 'dash' and player.state == 'active')):
				for h in hurtboxes:
					hb = h.box
					if (poly_collides(hb, new_p_box)):
						collisionhbs.append(h)

			# move if not colliding
			if (colliding):
				# test cardinal and diagonal moves for gliding
				possiblemoves = [
					(1, 0), (-1, 0), (0, 1), (0, -1),
					(0.70, 0.70), (-0.70, 0.70), 
					(-0.70, -0.70), (0.70, -0.70)
					]
				bestp = False
				bestpval = 0
				for i in range(8):
					move = possiblemoves[i]
					dotval = dot(move, new_dp)
					if (dotval > 0.6):
						test_p = [
							move[0]*speed + player.p[0], 
							move[1]*speed + player.p[1]]

						test_p_box = []
						for (sx, sy) in player.movebox:
							vx = sx + test_p[0]
							vy = sy + test_p[1]
							test_p_box.append((vx, vy))

						stillcollide = False
						for poly in collisionboxes:
							if (poly_collides(poly, test_p_box)):
								stillcollide = True
						if (not stillcollide and dotval > bestpval):
							bestp = test_p
							bestpval = dotval

				if (bestp != False): 
					player.p = bestp
				elif player.currentaction.actiontype == 'dash' and player.state == 'active':
					player.state = 'cooldown'
					player.actionframe = dashaction.cooldown + dashaction.chainframes
			else:
				player.p = new_p

		# calculate hurtboxes with enemies
		for h in hurtboxes:
			for e in entities:
				# only enemies can be hurt by hitboxes, no NPCs
				if (e.enemytype != None):
					if poly_collides(h.box, entity_get_hitbox(e)):
						entity_hurt(e, h, megabrain)
						h.destroy = True

		# clean hurtboxes
		for h in hurtboxes:
			hurtbox_update(h, geomap)
		hurtboxes = [h for h in hurtboxes if h.framesleft > 0 and not h.destroy]

		'''
		joystick = pygame.joystick.Joystick(0)
		joystick.init() # need this for the events to register at all
		'''

		# update logic based on collision and input
		player_update(player, hurtboxes)

		megabrain_update(megabrain, geomap, hurtboxes, player, screen)

		for e in entities:
			#entity_update_brain(e)
			entity_update_physics(e)
		# clean up entities
		entities = [e for e in entities if not e.DESTROY]

		# draw
		screen.fill(grey)

		# draw background dots
		joffset = int(tilewidth-player.p[1]%tilewidth) - tilewidth//2
		ioffset = int(tilewidth-player.p[0]%tilewidth) - tilewidth//2
		for j in range(joffset, screendim[1]+1, tilewidth):
			for i in range(ioffset, screendim[0]+1, tilewidth):
				pygame.draw.circle(screen, lightgrey, (i, j), 1, 1)

		# draw entities
		for y in range(geomap.height):
			for x in range(geomap.width):
				g = geomap.geo[y * geomap.width + x]
				if (g):
					newtile = [(x, y), ((x+1), y), ((x+1), (y+1)), (x, (y+1))]
					everts = [get_screen_coord(player.p, playeroffset, get_world_pos(p)) \
						for p in newtile]
					pygame.draw.polygon(screen, lightgrey, everts)

		for e in entities:
			everts = [get_screen_coord(player.p, playeroffset, (x+e.p[0], y+e.p[1])) \
				for (x, y) in e.hitbox]
			pygame.draw.polygon(screen, lightred, everts)

		pygame.draw.circle(screen, red, midscreen, 18)
		if player.currentaction.actiontype in ['attack', 'dash']:
			pygame.draw.circle(screen, darkred, midscreen, 18, 2)
		#pygame.draw.polygon(screen, red, )

		for h in hurtboxes:
			hverts = [get_screen_coord(player.p, playeroffset, p) for p in h.box]
			pygame.draw.polygon(screen, black, hverts, 1)

		global stufftodraw
		for h in stufftodraw:
			hverts = [get_screen_coord(player.p, playeroffset, p) for p in h]
			pygame.draw.polygon(screen, black, hverts, 1)

		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main()