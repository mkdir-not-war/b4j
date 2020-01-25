import pygame

def dot(v1, v2):
	return v1[0]*v2[0] + v1[1]*v2[1]

# treat like a struct
class Polygon:
	def __init__(self, vlist=[]):
		self.vertices = vlist[:]

def poly_contains(polygon, x, y):
	numverts = len(polygon.vertices)
	intersections = 0
	for i in range(numverts):
		x1 = polygon.vertices[i][0]
		y1 = polygon.vertices[i][1]
		x2 = polygon.vertices[(i+1)%numverts][0];
		y2 = polygon.vertices[(i+1)%numverts][1];

		if (((y1 <= y and y < y2) or
			(y2 <= y and y < y1)) and
			x < ((x2 - x1) / (y2 - y1) * (y - y1) + x1)):
			intersections += 1
	return (intersections & 1) == 1 

def poly_collides(poly1, poly2):
	for (x, y) in poly1.vertices:
		if (poly_contains(poly2, x, y)):
			return True
	for (x, y) in poly2.vertices:
		if (poly_contains(poly1, x, y)):
			return True
	return False

def get_screen_coord(playerpos, playeroff, worldx, worldy):
	diffx = worldx-playerpos[0]
	diffy = worldy-playerpos[1]
	return(playeroff[0]+diffx, playeroff[1]+diffy)

class Player:
	def __init__(self):
		self.p = [0, 0]
		self.dp = [0, 0]
		self.ddp = [0, 0]
		self.size = 1
		self.movebox = [] 

def main():
	pygame.init()

	grey = pygame.Color(200, 200, 200)
	lightgrey = pygame.Color(125, 125, 125)
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

	# populate walls
	wallwidth = 50

	for i in range(20):
		for j in range(20):
			if j == 0 or i == 0 or j == 19 or i == 19 or (i%j==4 and j != 15):
				geometry.append(Polygon(
					[(i*wallwidth, j*wallwidth), 
					((i+1)*wallwidth, j*wallwidth), 
					((i+1)*wallwidth, (j+1)*wallwidth), 
					(i*wallwidth, (j+1)*wallwidth)]
					))

	# player stuff
	playeroffset = midscreen
	player = Player()
	player.p = [100, 100]
	player.size = 40
	speed = 3.6
	# offset from player pos, as a factor of size
	player.movebox = [(.45, 0), (0, -0.45), (-0.45, 0), (0, 0.45)] 

	curr_input = [] # int list

	while not done:
		clock.tick(FPS)

		# poll input
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

		# movement calculation -> collision check -> update position
		if (not blocking):
			# skip accel/friction for now
			new_dp = [moveinput_dir[0]*speed, moveinput_dir[1]*speed]
			new_p = [new_dp[0] + player.p[0], new_dp[1] + player.p[1]]

			# check collision with new_p on geometry
			colliding = False
			collisionboxes = []
			new_p_box = Polygon()
			for (sx, sy) in player.movebox:
				vx = sx*player.size + new_p[0]
				vy = sy*player.size + new_p[1]
				new_p_box.vertices.append((vx, vy))

			for p in geometry:
				if (poly_collides(p, new_p_box)):
					colliding = True
					collisionboxes.append(p)

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

						test_p_box = Polygon()
						for (sx, sy) in player.movebox:
							vx = sx*player.size + test_p[0]
							vy = sy*player.size + test_p[1]
							test_p_box.vertices.append((vx, vy))

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

		'''
		joystick = pygame.joystick.Joystick(0)
		joystick.init() # need this for the events to register at all
		'''

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
				for (x, y) in e.vertices]
			pygame.draw.polygon(screen, lightgrey, everts)

		pygame.draw.circle(screen, red, midscreen, player.size//2)
		#pygame.draw.polygon(screen, red, )

		


		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main()