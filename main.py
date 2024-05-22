import math
import random
import sys
import os
import time

import neat
import neat.config
import pygame

#Map (from 1 to 5, increasing in difficulty)

MAP = 'map2.png'

#Constants

WIDTH = 1920
HEIGHT = 1080

BORDER = 120

CAR_START_X = 830
CAR_START_Y = 920

CAR_SIZE_X = 50
CAR_SIZE_Y = 50

DEFAULT_SPEED = 20
MIN_SPEED = 12
SPEED_CHANGE = 2

TURN_ANGLE = 10

#The color the cars should not touch

BAD_COLOR = (255, 255, 255, 255)
SENSOR_COLOR = (0, 255, 0)

MAX_SENSOR_LENGTH = 300

current_generation = 0

def distance2d(x1, y1, x2, y2):
	delta_x = x1 - x2
	delta_y = y1 - y2
	return int(math.sqrt(delta_x * delta_x + delta_y * delta_y))

class Car:

	def __init__(self):
		self.sprite = pygame.image.load('car.png')
		self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
		self.rotated_sprite = self.sprite

		self.position = [CAR_START_X, CAR_START_Y]
		self.angle = 0
		self.speed = 0

		self.speed_set = False
		self.update_center()

		#we store the coordonates and the distance from the border of the sensors
		self.sensors = []

		self.alive = True

		#Distance driven and time passed
		self.distance = 0
		self.time = 0

	def update_center(self):
		self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

	def draw(self, screen):
		screen.blit(self.rotated_sprite, self.position)
		self.draw_sensors(screen)

	def draw_sensors(self, screen):
		for sensor in self.sensors:
			position = sensor[0]
			pygame.draw.line(screen, SENSOR_COLOR, self.center, position, 1)
			pygame.draw.circle(screen, SENSOR_COLOR, position, 5)

	def check_collision(self, game_map):
		self.alive = True

		#we only have to check for the corners, not for the entire car
		for point in self.corners:
			if game_map.get_at((int(point[0]), int(point[1]))) == BAD_COLOR:
				self.alive = False
				break

	def update_sensor(self, sensor_angle, game_map):
		length = 0

		x = int(self.center[0] + math.cos(math.radians(360 - (sensor_angle + self.angle))) * length)
		y = int(self.center[1] + math.sin(math.radians(360 - (sensor_angle + self.angle))) * length)

		while game_map.get_at((x, y)) != BAD_COLOR and length < MAX_SENSOR_LENGTH:
			length += 1
			x = int(self.center[0] + math.cos(math.radians(360 - (sensor_angle + self.angle))) * length)
			y = int(self.center[1] + math.sin(math.radians(360 - (sensor_angle + self.angle))) * length)

		dist = distance2d(x, y, self.center[0], self.center[1])

		self.sensors.append([(x, y), dist])

	def update_sensors(self, game_map):
		for angle in range(-90, 120, 45):
			self.update_sensor(angle, game_map)

	#dont let the car get too close to the map limits
	def correct_positions(self):
		self.position[0] = min(self.position[0], WIDTH - BORDER)
		self.position[1] = min(self.position[1], HEIGHT - BORDER)
		self.position[0] = max(self.position[0], BORDER)
		self.position[1] = max(self.position[1], BORDER)

	def rotate_center(self, image, angle):
		rectangle = image.get_rect()
		rotated_image = pygame.transform.rotate(image, angle)
		rotated_rectangle = rectangle.copy()
		rotated_rectangle.center = rotated_image.get_rect().center
		rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
		return rotated_image

	def update(self, game_map):
		if not self.speed_set:
			self.speed = DEFAULT_SPEED
			self.speed_set = True

		self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
		self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
		self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
		#self.correct_positions()
		self.update_center()	

		self.distance += self.speed
		self.time += 1

		#calculate the 4 corners
		length = 0.5 * CAR_SIZE_X

		left_top 			= [self.center[0] + math.cos(math.radians(360 - (self.angle + 30)))  * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30)))  * length]
		right_top 		= [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
		left_bottom 	= [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
		right_bottom	= [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
		self.corners 	= [left_top, right_top, left_bottom, right_bottom]

		self.check_collision(game_map)
		
		self.sensors.clear()
		self.update_sensors(game_map)

	def is_alive(self):
		return self.alive
	
	def get_reward(self):
		return self.distance / (CAR_SIZE_X / 2)
	
	def get_data(self):
		sensors = self.sensors
		sensor_data = [0, 0, 0, 0, 0]
		for i, sensor in enumerate(sensors):
			sensor_data[i] = int(sensor[1] / 30)
		return sensor_data


def run_simulation(genomes, config):
	networks = []
	cars = []

	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

	for i, genome in genomes:
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		networks.append(net)
		genome.fitness = 0
		cars.append(Car())

	clock = pygame.time.Clock()
	generation_font = pygame.font.SysFont("Arial", 30)
	alive_font = pygame.font.SysFont("Arial", 20)
	game_map = pygame.image.load(MAP).convert()

	global current_generation
	current_generation += 1

	start_timer = time.time()

	while True:
		skip_generation = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit(0)
				elif event.key == pygame.K_SPACE:
					skip_generation = True
					break
		
		if skip_generation:
			break

		for i, car in enumerate(cars):
			#add our sensor data into the network
			output = networks[i].activate(car.get_data())

			#choose the best choice
			# 0 = left
			# 1 = right
			# 2 - speed up
			# 3 - slow down
			choice = output.index(max(output))

			if choice == 0:
				car.angle += TURN_ANGLE
			elif choice == 1:
				car.angle -= TURN_ANGLE
			elif choice == 2:
				car.speed += SPEED_CHANGE
			elif car.speed - SPEED_CHANGE >= MIN_SPEED:
				car.speed -= SPEED_CHANGE

		cars_alive = 0
		for i, car in enumerate(cars):
			if car.is_alive():
				cars_alive += 1
				car.update(game_map)
				genomes[i][1].fitness += car.get_reward()

		#all cars are dead or too much time elapsed
		if cars_alive == 0 or time.time() - start_timer > 25:
			break
		
		screen.blit(game_map, (0, 0))
		for car in cars:
			if car.is_alive():
				car.draw(screen)

		#Generation and car counter texts

		text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
		text_rect = text.get_rect()
		text_rect.center = (900, 450)
		screen.blit(text, text_rect)

		text = alive_font.render("Still Alive: " + str(cars_alive), True, (0, 0, 0))
		text_rect = text.get_rect()
		text_rect.center = (900, 490)
		screen.blit(text, text_rect)

		pygame.display.flip()  
		clock.tick(60)  # Run at 60 frames per second
	
	pygame.quit() 

if __name__ == "__main__":
	config_path = "./config.txt"
	config = neat.config.Config(neat.DefaultGenome,
														  neat.DefaultReproduction,
														  neat.DefaultSpeciesSet,
														  neat.DefaultStagnation,
														  config_path)
	
	population = neat.Population(config)
	population.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	population.add_reporter(stats)
	
	population.run(run_simulation, 1000)

