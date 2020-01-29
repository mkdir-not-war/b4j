import pygame
from math import sqrt

def dot(v1, v2):
	return v1[0]*v2[0] + v1[1]*v2[1]

def length(v):
	return sqrt(v[0]**2 + v[1]**2)

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

# treat like a struct
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

def get_screen_coord(playerpos, playeroff, worldx, worldy):
	diffx = worldx-playerpos[0]
	diffy = worldy-playerpos[1]
	return(playeroff[0]+diffx, playeroff[1]+diffy)

class Entity:
	def __init__(self, pos):
		self.p = pos[:]
		self.hitbox = None

def entity_get_hitbox(entity):
	return [(x+entity.p[0], y+entity.p[1]) for (x, y) in entity.hitbox]

class Hurtbox:
	def __init__(self, box, frames, dir):
		self.box = box[:]
		self.framesleft = frames
		self.direction = dir

def hurtbox_get(box, direction, position, frames):
	hb = get_rotated_vecs(direction, box)
	hb = [(x+position[0], y+position[1]) for (x, y) in hb]
	return Hurtbox(hb, frames, direction)

class NoneAction:
	def __init__(self):
		self.actiontype = 'none'

noneaction = NoneAction()

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

		self.jab = None
		self.uppercut = None

def player_update(player, hurtboxes):
	if (player.actionframe > 0):
		player.actionframe -= 1
	if (player.actionframe <= 0):
		if player.currentaction.actiontype == 'attack':
			if player.state == 'startup':
				player.state = 'hurt'
				player.actionframe = player.currentaction.hurtframes
				hurtbox = [(x*player.size, y*player.size) \
					for (x, y) in player.currentaction.box]
				hurtboxes.append(hurtbox_get(
					hurtbox, 
					player.dir, 
					player.p, 
					player.currentaction.hurtframes))
			elif player.state == 'hurt':
				player.state = 'cooldown'
				player.actionframe = player.currentaction.cooldown
			elif player.state == 'cooldown':
				player.state = 'idle'
				player.currentaction = noneaction
				

def player_attack(player, attack):
	player.state = 'startup'
	player.currentaction = attack

class Attack:
	def __init__(self, startup, hurtframes, cooldown, box, nextatk=None):
		self.actiontype = 'attack'
		self.startup = startup # frames int
		self.hurtframes = hurtframes # frames int
		self.cooldown = cooldown # frames int
		self.box = box # use hurtbox_get to create object
		self.nextatk = nextatk # auto-start this next if not None

def main():
	pygame.init()

	grey = pygame.Color(200, 200, 200)
	lightgrey = pygame.Color(125, 125, 125)
	darkred = pygame.Color(80, 0, 0)
	lightred = pygame.Color(250, 100, 100)
	red = pygame.Color('red')
	black = pygame.Color('black')

	# Set the width and height of the screen (width, height).
	screendim = (700, 500)
	midscreen = (350, 250)
	screen = pygame.display.set_mode(screendim)
	pygame.display.set_caption("B4J prototype")

	done = False
	clock = pygame.time.Clock()
	FPS = 30

	pygame.joystick.init()

	geometry = []
	entities = []
	hurtboxes = []

	# populate walls
	wallwidth = 50

	for i in range(20):
		for j in range(20):
			if j == 0 or i == 0 or j == 19 or i == 19 or (i%j==4 and j != 15):
				geometry.append(
					[(i*wallwidth, j*wallwidth), 
					((i+1)*wallwidth, j*wallwidth), 
					((i+1)*wallwidth, (j+1)*wallwidth), 
					(i*wallwidth, (j+1)*wallwidth)]
					)

	# throw in a couple baddies
	baddy1 = Entity([150, 150])
	baddy1.hitbox = [(-20, -20), (-20, 20), (20, 20), (20, -20)]
	entities.append(baddy1)

	# player stuff
	playeroffset = midscreen
	player = Player()
	player.p = [100, 100]
	player.size = 40 # aka diameter
	speed = 3.7
	player.dir = (0, 1)
	# offset from player pos, as a factor of size
	player.movebox = [(.45, 0), (0, -0.45), (-0.45, 0), (0, 0.45)] 

	player.jab = Attack(
		1, 3, 5, 
		[(0.55, 0.30), (1.20, 0.30), (1.20, -0.30), (0.55, -0.30)])
	player.uppercut = Attack(
		24, 6, 24,
		[(0.55, 0.30), (1.20, 0.30), (1.20, -0.30), (0.55, -0.30)])


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
		blocking = False
		if pygame.K_ESCAPE in curr_input:
			done = True
		if player.state == 'idle':
			if pygame.K_SPACE in curr_input:
				blocking = True

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
				player.dir = moveinput_dir[:]

			if pygame.K_KP0 in curr_input and not pygame.K_KP0 in prev_input:
				player_attack(player, player.jab)
			elif pygame.K_KP1 in curr_input and not pygame.K_KP1 in prev_input:
				player_attack(player, player.uppercut)

		elif player.state == 'dashing':
			pass # can skip the cooldown period

		elif player.state == 'blocking':
			if ((pygame.K_KP0 in curr_input and not pygame.K_KP0 in prev_input) or
				(pygame.K_KP1 in curr_input and not pygame.K_KP1 in prev_input)):
				pass # attempt to parry

		# movement calculation -> collision check -> update position
		if (not blocking):
			# skip accel/friction for now
			new_dp = [moveinput_dir[0]*speed, moveinput_dir[1]*speed]
			new_p = [new_dp[0] + player.p[0], new_dp[1] + player.p[1]]

			# check collision with new_p on geometry, entities and hurtboxes
			colliding = False
			collisionboxes = []
			collisionentities = []
			collisionhbs = []

			new_p_box = []
			for (sx, sy) in player.movebox:
				vx = sx*player.size + new_p[0]
				vy = sy*player.size + new_p[1]
				new_p_box.append((vx, vy))

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
							vx = sx*player.size + test_p[0]
							vy = sy*player.size + test_p[1]
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
			else:
				player.p = new_p

		# calculate hurtboxes with enemies

		# clean hurtboxes
		for h in hurtboxes:
			h.framesleft -= 1
		hurtboxes = [h for h in hurtboxes if h.framesleft > 0]

		'''
		joystick = pygame.joystick.Joystick(0)
		joystick.init() # need this for the events to register at all
		'''

		# update logic based on collision and input
		player_update(player, hurtboxes)

		# draw
		screen.fill(grey)

		# draw background grid
		gridwidth = 50
		gridoffx = gridwidth - player.p[0]%gridwidth
		gridoffy = gridwidth - player.p[1]%gridwidth
		i = gridoffx
		while i <= 700:
			pygame.draw.line(screen, lightgrey, (i, 0), (i, 501))
			i += gridwidth

		j = gridoffy
		while j <= 500:
			pygame.draw.line(screen, lightgrey, (0, j), (701, j))
			j += gridwidth

		# draw entities
		for e in geometry:
			everts = [get_screen_coord(player.p, playeroffset, x, y) \
				for (x, y) in e]
			pygame.draw.polygon(screen, lightgrey, everts)

		for e in entities:
			everts = [get_screen_coord(player.p, playeroffset, x+e.p[0], y+e.p[1]) \
				for (x, y) in e.hitbox]
			pygame.draw.polygon(screen, lightred, everts)

		pygame.draw.circle(screen, red, midscreen, player.size//2)
		if player.currentaction.actiontype == 'attack':
			pygame.draw.circle(screen, darkred, midscreen, player.size//2, 2)
		#pygame.draw.polygon(screen, red, )

		for h in hurtboxes:
			hverts = [get_screen_coord(player.p, playeroffset, x, y) for (x, y) in h.box]
			pygame.draw.polygon(screen, black, hverts, 1)


		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main()