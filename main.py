import pygame

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

def main():
	pygame.init()

	grey = pygame.Color(200, 200, 200)
	lightgrey = pygame.Color(125, 125, 125)
	red = pygame.Color('red')
	black = pygame.Color('black')

	# Set the width and height of the screen (width, height).
	screen = pygame.display.set_mode((700, 500))
	pygame.display.set_caption("B4J prototype")

	done = False
	clock = pygame.time.Clock()
	FPS = 30

	pygame.joystick.init()



	# player stuff
	playeroffset = (250, 350)
	playerpos = [120, 120]
	playerwidth = 40
	speed = 3.5

	curr_input = []

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
		if pygame.K_ESCAPE in curr_input:
			done = True
		if pygame.K_UP in curr_input:
			playerpos[1] -= speed
		if pygame.K_DOWN in curr_input:
			playerpos[1] += speed
		if pygame.K_LEFT in curr_input:
			playerpos[0] -= speed
		if pygame.K_RIGHT in curr_input:
			playerpos[0] += speed

		# handle input
		'''
		joystick = pygame.joystick.Joystick(0)
		joystick.init() # need this for the events to register at all
		'''

		# draw
		screen.fill(grey)

		# draw background grid
		gridwidth = 50
		gridoffx = gridwidth - playerpos[0]%gridwidth
		gridoffy = gridwidth - playerpos[1]%gridwidth
		i = gridoffx
		while i <= 700:
			pygame.draw.line(screen, lightgrey, (i, 0), (i, 501))
			i += gridwidth

		j = gridoffy
		while j <= 500:
			pygame.draw.line(screen, lightgrey, (0, j), (701, j))
			j += gridwidth

		# draw entities
		pygame.draw.circle(screen, red, (350, 250), playerwidth//2)
		#pygame.draw.polygon(screen, red, )

		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main()