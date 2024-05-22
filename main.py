import math
import random
import sys
import os

import neat
import pygame

#Constants

WIDTH = 1920
HEIGHT = 1080

BORDER = 20

CAR_START_X = 830
CAR_START_Y = 920

CAR_SIZE_X = 50
CAR_SIZE_Y = 50

DEFAULT_SPEED = 20
MIN_SPEED = 12

#The color the cars should not touch

BAD_COLOR = (255, 255, 255, 255)
SENSOR_COLOR = (0, 255, 0)

MAX_SENSOR_LENGTH = 300

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
		self.drawing_sensors = []

		self.alive = True

		#Distance driven and time passed
		self.distance = 0
		self.time = 0

	def update_center(self):
		self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]

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
			if game_map.get_at(int(point[0]), int(point[1])) == BAD_COLOR:
				self.alive = False
				break

	def update_sensor(self, sensor_angle, game_map):
		length = 0
		center_x = self.center[0]
		center_y = self.center[1]
		total_angle = math.radians(sensor_angle + self.angle)
		
		x = 0
		y = 0

		def update_coords():
			nonlocal x
			nonlocal y
			x = int(center_x + math.cos(total_angle) * length)
			y = int(center_y + math.sin(total_angle) * length)

		update_coords()

		while game_map.get_at((x, y)) != BAD_COLOR and length < MAX_SENSOR_LENGTH:
			length += 1
			update_coords()
			print(x, y);

		dist = distance2d(x, y, center_x, center_y)

		self.sensors.append([(x, y), dist])

	def update_sensors(self, game_map):
		for angle in range(-90, 120, 45):
			self.update_sensors(angle, game_map)

	#dont let the car get too close to the map limits
	def correct_positions(self):
		self.position[0] = min(self.position[0], WIDTH - BORDER)
		self.position[1] = min(self.position[1], HEIGHT - BORDER)
		self.position[0] = max(self.position[0], BORDER)
		self.position[1] = max(self.position[1], BORDER)

	def update(self, game_map):
		if not self.speed_set:
			self.speed = DEFAULT_SPEED
			self.speed_set = True

		self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
		self.position[0] += math.cos(math.radians(self.angle)) * self.speed
		self.position[1] += math.sin(math.radians(self.angle)) * self.speed
		self.correct_positions()
		self.update_center()

		self.distance += self.speed
		self.time += 1

		

def run_simulation():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	game_map = pygame.image.load('map.png').convert()
	car = Car()

	clock = pygame.time.Clock() 

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

		screen.blit(game_map, (0, 0))

		#print(car.position)
		
		car.update_sensors(game_map)
		car.draw(screen)

		pygame.display.flip() 
	
		clock.tick(60)  # Run at 60 frames per second
	
	pygame.quit() 

if __name__ == "__main__":
	run_simulation()

