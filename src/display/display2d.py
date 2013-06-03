# -*- coding:utf-8 -*-
import pygame, sys
from pygame.locals import *

from dcel import dcel
from utils import Vector

import algoritmos

import threading, random

class InterfaceThread(threading.Thread):
    def __init__(self, dcel):
        threading.Thread.__init__(self)
        self.interface = Interface(dcel)
        self.daemon = True

    def run(self):
        self.interface.start()

class Interface:
    def __init__(self, dcel = None, size = (800, 600), discoteca = False):
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.Font("../media/font/VeraMono.ttf", 20)
        self.init_display(size)

        self.running = True
        self.dcel = dcel
        self.discoteca = discoteca

        self.selected = 0
        self.image_count = 0
        self.clock = pygame.time.Clock()

    def init_display(self, size):
        self.size = size
        width, height = size

        self.screen = pygame.display.set_mode(size)
        # Icon and window title
        pygame.display.set_caption("Rivendel")

#        icon = pygame.image.load("../media/icon.png").convert_alpha()
#        icon = pygame.transform.smoothscale(icon,(32,32))
#        pygame.display.set_icon(icon)


    def draw(self):
        self.screen.fill((200,200,200))

        if self.dcel and self.dcel.vertices and self.dcel.edges and self.dcel.faces:
            coords = [v.coordinates.z for v in self.dcel.vertices]
            m = min(coords)
            M = max(coords)

            vertex_color = lambda v: int(((v.coordinates.z - m) / (M - m + 1e-15)) * 255)
            coordinates = lambda v: (int(v.coordinates.x * 600 + 100),
                                     int(v.coordinates.y * 400 + 100))

            if self.discoteca:
                self.screen.fill((0,0,0))
                coordinates = lambda v: (int(v.coordinates.x * 800),
                                         int(v.coordinates.y * 600))

                for f in self.dcel.faces:
                    vertices = map(coordinates, f.vertices)
                    color = [random.randint(0,200), random.randint(0,200), random.randint(0,200)]
                    pygame.draw.polygon(self.screen, color, vertices)


            else:
                text = self.font.render("%d vertices" % len(self.dcel.vertices), True, (0,0,0))
                dest = self.screen.get_rect()
                self.screen.blit(text, dest)#, self.screen.get_rect())



                # selected edge
                s = self.dcel.edges[self.selected]

                color = [0, 0, 100]
                for f in self.dcel.faces:
                    vertices = map(coordinates, f.vertices)
                    pygame.draw.polygon(self.screen, color, vertices)
                    color[2] += 77
                    color[2] %= 256

                # selected edge faces
                if s.face:
                    vertices = map(coordinates, s.face.vertices)
                    pygame.draw.polygon(self.screen, [50,0,0], vertices)
                if s.twin.face:
                    vertices = map(coordinates, s.twin.face.vertices)
                    pygame.draw.polygon(self.screen, [150,0,0], vertices)

                for e in self.dcel.edges:
                    vertices = map(coordinates, e.vertices)

                    color = [0,255,0]
                    pygame.draw.line(self.screen, color, vertices[0],
                                     vertices[1])

                for v in self.dcel.vertices:
                    pos = coordinates(v)
                    vc = vertex_color(v)
                    if vc > 255: vc = 255
                    if vc < 0:   vc = 0
                    color = [vc,vc,vc]
                    pygame.draw.circle(self.screen, (0,0,0), pos, 5)
                    pygame.draw.circle(self.screen, color, pos, 4)

                # render selected
                for v in s.vertices:
                    pos = coordinates(v)
                    pygame.draw.circle(self.screen, (255,0,0), pos, 3)

                vertices = map(coordinates, s.vertices)
                color = [255,0,0]
                pygame.draw.line(self.screen, color, vertices[0],
                                 vertices[1])

        pygame.display.flip()


    def process_event(self, event):
        # Mouse
        if event.type == MOUSEBUTTONDOWN:
            coordinates = lambda p: Vector((p[0] - 100) / 600.,
                                           (p[1] - 100) / 400.,
                                           0)

            face = self.dcel.find_face(coordinates(event.pos))
            if face:
                self.selected = self.dcel.edges.index(face.edge)

        # Keyboard
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.stop()
            elif event.key == K_SPACE:
                e = self.dcel.edges[self.selected]
                if event.mod & KMOD_SHIFT > 0:
                    self.selected = self.dcel.edges.index(e.next)
                else:
                    self.selected = self.dcel.edges.index(e.prev)


            elif event.key == K_f:
                self.dcel.edges[self.selected].flip()
        elif event.type == QUIT:
            self.stop()


    def loop(self):
        event = pygame.event.poll()
        while event.type != NOEVENT:
            self.process_event(event)
            event = pygame.event.poll()

        self.draw()
        return self.running


    def start(self):
        while self.loop() and self.running:
            pass

    def stop(self):
        print "Stopping interface..."
        self.running = False
