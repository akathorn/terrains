# -*- coding:utf-8 -*-
import pygame, sys
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from dcel import dcel
from utils import Vector

import algoritmos


def renderString(x, y, string):
    glColor3f(0,0,0)
    glRasterPos2f(x, y);
    for c in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, c_int(ord(c)))


class Interface:
    def __init__(self, dcel = None, size = (800, 600), mode3d = False):
        pygame.init()
#        pygame.font.init()

        self.mode3d = mode3d

#        self.font = pygame.font.Font("../media/font/VeraMono.ttf", 20)
        self.init_display(size)

        self.running = True
        self.dcel = dcel

        self.selected = 0
        self.clock = pygame.time.Clock()

        if self.mode3d:
            self.draw = self.draw3d
        else:
            self.draw = self.draw2d


    def init_display(self, size):
        self.size = size
        width, height = size

        flags = RESIZABLE
        if self.mode3d:
            flags = flags|DOUBLEBUF|OPENGL|HWSURFACE

        self.screen = pygame.display.set_mode(size, flags)
        if self.mode3d:
            self.init3d(size)

        # Icon and window title
        pygame.display.set_caption("Rivendel")

#        icon = pygame.image.load("../media/icon.png").convert_alpha()
#        icon = pygame.transform.smoothscale(icon,(32,32))
#        pygame.display.set_icon(icon)


    def init3d(self, size):
        self.resize(size[0], size[1])
        glEnable(GL_DEPTH_TEST)

#        glShadeModel(GL_FLAT)
        glClearColor(0.8, 0.8, 0.8, 0.0)

        # glEnable(GL_COLOR_MATERIAL)

        # glEnable(GL_LIGHTING)
        # glEnable(GL_LIGHT0)
        # glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))

    def draw3d(self):
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw outlines only
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        glColor(0,0,0)
        # Draw some stuff
        glBegin(GL_TRIANGLES)
        glVertex2i(50, 50)
        glVertex2i(75, 100)
        glVertex2i(200, 200)
        glEnd()

#         # Clear buffers
#         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

#         # glMatrixMode(GL_PROJECTION)
#         # glLoadIdentity()
#         # gluPerspective(90, (640. / 480), 0.0001, 200000)

#         # glMatrixMode(GL_MODELVIEW)
# #        glLoadIdentity();

#         renderString(10, 10, "Hola")

# #         gluLookAt(0, 1, 1.2, 0, 0, 0, 0, 0, 1)

# #         # Draw outlines only
# # #        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

# #         # Draw some stuff
# #         glBegin(GL_POINTS)
# #         if self.dcel and self.dcel.vertices:
# #             m = min([v.coordinates.z for v in self.dcel.vertices])
# #             M = max([v.coordinates.z for v in self.dcel.vertices])
# #             for v in self.dcel.vertices:
# #                 p = v.coordinates
# #                 glVertex3f(p.x, p.y, p.z)
# #         glEnd()
        pygame.display.flip()

    def draw2d(self):
        self.screen.fill((200,200,200))

        if not self.dcel.vertices:
            return

        m = min([v.coordinates.z for v in self.dcel.vertices])
        M = max([v.coordinates.z for v in self.dcel.vertices])

        coordinates = lambda v: (int(v.coordinates.x * 600 + 100),
                                 int(v.coordinates.y * 400 + 100))

        vertex_color = lambda v: int((v.coordinates.z - m) / (M - m + 1) * 255)

        if self.dcel:
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

            # for e in algoritmos.rios(self.dcel):
            #     vertices = map(coordinates, e.vertices)

            #     color = [255,0,255]
            #     pygame.draw.line(self.screen, color, vertices[0],
            #                      vertices[1])


        pygame.display.flip()


    def process_event(self, event):
        # Mouse
        if event.type == MOUSEBUTTONDOWN:
            coordinates = lambda p: Vector((p[0] - 100) / 600.,
                                           (p[1] - 100) / 400.,
                                           0)

            if self.dcel:
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

        # Varios
        elif event.type == QUIT:
            self.stop()
        elif event.type == VIDEORESIZE:
            self.resize(event.w, event.h)


    def loop(self):
        event = pygame.event.poll()
        while event.type != NOEVENT:
            self.process_event(event)
            event = pygame.event.poll()

        self.draw()
        return self.running


    def resize(self, width, height):
        if self.mode3d:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(60.0, float(width)/height, .1, 1000.)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

    def start(self):
        while self.loop() and self.running:
            pass

    def stop(self):
        print "Stopping interface..."
        self.running = False
