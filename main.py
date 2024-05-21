import math
import random
import sys
import os

import neat
import pygame

#Constants

WIDTH = 1600
HEIGHT = 880

CAR_START_X = 830
CAR_START_Y = 920

CAR_SIZE_X = 50
CAR_SIZE_Y = 50

#The color the cars should not touch

BAD_COLOR = (255, 255, 255, 255)
SENSOR_COLOR = (0, 255, 0)

class Car:

	def __init__(self):
		self.sprite = pygame.image.load('car.png')
		self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
		self.rotated_sprite = self.sprite

		self.position = [CAR_SIZE_X, CAR_SIZE_Y]
		self.angle = 0
		self.speed = 0

		self.speed_set = False
		self.center = [CAR_START_X + CAR_SIZE_X / 2, CAR_START_Y + CAR_START_Y / 2]

		self.sensors = []
		self.drawing_sensors = []

		self.alive = True

		#Distance driven and time passed
		self.distance = 0
		self.time = 0

	def draw(self, screen):
		screen.blit(self.rotated_sprite, self.position)
		self.draw_sensors(screen)

	def draw_sensors(self, screen):
		for sensor in self.sensors:
			position = sensor[0]
			pygame.draw.line(screen, SENSOR_COLOR, self.center, position, 1)
			pygame.draw.circe(screen, SENSOR_COLOR, position, 5)

	def check_collision(self, game_map):
		self.alive = True

		#we only have to check for the corners, not for the entire car
		for point in self.corners:
			if game_map.get_at(int(point[0]), int(point[1])) == BAD_COLOR:
				self.alive = False
				break
	
	def update_sensors(self, degree, game_map):
		length = 0
		center_x = self.center[0]
		center_y = self.center[1]
		x = int(center_x )


  

