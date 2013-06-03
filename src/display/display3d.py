import sys

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from math import radians
from opengl_utils.matrix44 import *

from dcel import Edge, Face, Vertex

import readline


class CallList:
	def __init__(self, fun = None, args = None):
		self._id = glGenLists(1)
		self._valid = False
		self._update_fun = fun
		self._update_args = args

	def draw(self):
		if self._valid:
			glCallList(self._id)
		else:
			if self._update_fun is not None:
				self.update()

	def lazy_update(self):
		self._valid = False

	def update(self):
		self.start(GL_COMPILE)#_AND_EXECUTE)
		if self._update_args is not None:
			self._update_fun(*self._update_args)
		else:
			self._update_fun()
		self._valid = True
		self.end()

	def start(self, _call = GL_COMPILE):
		glNewList(self._id, _call)

	def end(self):
		glEndList()

	def __del__(self):
		if glDeleteLists is not None: glDeleteLists(self._id,1)

class Interface:
    def __init__(self, dcel = None, size = (800, 600), inbuff = None,
                 outbuff = None):
        self.dcel = dcel
        self.running = True

        pygame.init()
        screen = pygame.display.set_mode(size, HWSURFACE|OPENGL|DOUBLEBUF)

        self.size = size
        self.resize(*size)
        self.init()

        self.clock = pygame.time.Clock()
        self.inbuff  = inbuff
        self.outbuff = outbuff

        glMaterial(GL_FRONT, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
        glMaterial(GL_FRONT, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

        # Camera transform matrix
        self.camera_matrix = Matrix44()
        self.camera_matrix.translate = (0.5, 0.7, 1.4)

        rotation_matrix = Matrix44.xyz_rotation(-0.7, 0, 0)
        self.camera_matrix *= rotation_matrix


        # Initialize speeds and directions
        self.rotation_direction = Vector3()
        self.rotation_speed = radians(0.5)
        self.movement_direction = Vector3()
        self.movement_speed = 1.0

        self.navigation = True
        self.toggle_navigation_mode()


        # cache
        self.cache_cooldown = 0
        self.call_list = CallList(self.draw_dcel)

        self.highlight = []
        self._show_faces = True
        self._show_edges = True

        self.update = True

        self.zscale = 1

    def init(self):
        glutInit()

        glEnable(GL_DEPTH_TEST)

        glShadeModel(GL_FLAT)
        glClearColor(0.5, 0.5, 0.5, 0.0)

        glEnable(GL_COLOR_MATERIAL)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_POSITION,  (1, 1, 0, 0))


    def loop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.stop()
            if event.type == KEYUP and event.key == K_ESCAPE:
                self.stop()
            if event.type == KEYDOWN:
                if event.key == K_LCTRL or event.key == K_LCTRL:
                    self.toggle_navigation_mode()
                elif not self.navigation:
                    if event.key == K_RETURN:
                        readline.insert_text(event.unicode.decode())
                        readline.redisplay()
                    else:
                        readline.insert_text(event.unicode.decode())
                        readline.redisplay()


        # Clear the screen, and z-buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        time_passed = self.clock.tick(30)
        time_passed_seconds = time_passed / 1000.

        # # Reset rotation and movement directions
        self.rotation_direction.set(0.0, 0.0, 0.0)
        self.movement_direction.set(0.0, 0.0, 0.0)

        pressed = pygame.key.get_pressed()

        if self.navigation:
            if pressed[K_e]:
                self.rotation_direction.z = -100.0
            elif pressed[K_q]:
                self.rotation_direction.z = +100.0
            if pressed[K_w]:
                self.movement_direction.z = -1.0
            elif pressed[K_s]:
                self.movement_direction.z = +1.0
            if pressed[K_a]:
                self.movement_direction.x = -1.0
            elif pressed[K_d]:
                self.movement_direction.x = +1.0

            if pressed[K_LSHIFT]:
                self.movement_direction *= 0.01

            # if pressed[K_PLUS]:
            #     self.zscale += 10
            #     self.update = True
            # if pressed[K_MINUS]:
            #     self.zscale -= 10
            #     self.update = False

            # Mouse
            (x,y) = map(float, pygame.mouse.get_rel())
            self.rotation_direction.x = -y
            self.rotation_direction.y = -x



        # Calculate rotation matrix and multiply by camera matrix
        rotation = self.rotation_direction * self.rotation_speed \
                   * time_passed_seconds

        rotation_matrix = Matrix44.xyz_rotation(*rotation)
        self.camera_matrix *= rotation_matrix

        # Calcluate movment and add it to camera matrix translate
        heading = Vector3(self.camera_matrix.forward)
        movement = heading * self.movement_direction.z * self.movement_speed
        self.camera_matrix.translate += movement * time_passed_seconds

        right = Vector3(self.camera_matrix.right)
        movement = right * self.movement_direction.x * self.movement_speed
        self.camera_matrix.translate += movement * time_passed_seconds



        # # Upload the inverse camera matrix to OpenGL
        glLoadMatrixd(self.camera_matrix.get_inverse().to_opengl())

        # # Light must be transformed as well
        glLight(GL_LIGHT0, GL_POSITION,  (0, 1.5, 1, 0))


        self.cache_cooldown -= time_passed
        if (self.cache_cooldown < 0 and self.dcel and self.dcel.updated) or self.update:
            self.cache_cooldown = 1000
            self.call_list.lazy_update()
            self.dcel.updated = False
            self.update = False


        self.call_list.draw()


        if self.outbuff:
            self.draw_text(self.outbuff.getvalue(), 0, 0)


        data = str(self.camera_matrix.translate) + "\n" + \
               str(self.camera_matrix.forward)
        self.draw_text(data, 0,
                       self.size[1]-10)

        # Show the screen
        pygame.display.flip()

        return self.running


    def draw_dcel(self):
        if self._show_faces and self.dcel and self.dcel.faces:
            self.draw_faces(self.dcel.faces, (1,1,1))

        if self._show_edges and self.dcel and self.dcel.edges:
            self.draw_edges(self.dcel.edges, (0,0,0))

        if self.highlight:
            if isinstance(self.highlight[0], Edge):
                self.draw_edges(self.highlight, (0,0,1))
            elif isinstance(self.highlight[0], Face):
                self.draw_faces(self.highlight, (1,0,0))


    def draw_faces(self, faces, *color):
        glBegin(GL_TRIANGLES)
        glColor3fv(color)
        for f in faces:
            nv = f.normalvect
            glNormal3f( nv.x, nv.z * self.zscale, nv.y )
            vertices = [v.coordinates for v in f.vertices]

            for v in vertices:
                glVertex3f(v.x, v.z * self.zscale, v.y)
        glEnd()

    def draw_edges(self, edges, *color):
        glBegin(GL_LINES)
        glColor3fv(color)
        for e in edges:
            vertices = [v.coordinates for v in e.vertices]
            for v in vertices:
                glVertex3f(v.x, v.z  * self.zscale + 1e-10, v.y)
        glEnd()


    def resize(self, width, height):
        self.size = (width, height)

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, float(width)/height, .0001, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def start(self):
        while self.loop():
            pass

    def stop(self):
        print "Stopping interface..."
        self.running = False
        self.toggle_navigation_mode(False)


    def toggle_navigation_mode(self, to = None):
        if to != None:
            self.navigation = to
        else:
            self.navigation = not self.navigation

        pygame.mouse.set_visible(not self.navigation)
        pygame.event.set_grab(self.navigation)



    def draw_text(self, value, x, y, step = 10):
        glMatrixMode(GL_PROJECTION);
        # For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
        # glPushMatrix()
        matrix = glGetDouble( GL_PROJECTION_MATRIX )

        height, width = self.size

        glLoadIdentity();
        glOrtho(0.0, height, 0.0, width, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity();
        glRasterPos2i(x, y);
        lines = 0

        for character in value:
            if character == '\n':
                lines += 1
                glRasterPos2i(x, y-(lines*step))
            else:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(character));

        glPopMatrix();
        glMatrixMode(GL_PROJECTION);

        # For some reason the GL_PROJECTION_MATRIX is overflowing with a single push!
        # glPopMatrix();
        glLoadMatrixd( matrix ) # should have un-decorated alias for this...

        glMatrixMode(GL_MODELVIEW);


    def show(self, things):
        self.highlight = things
        self.update = True

    def show_edges(self, show = True):
        self._show_edges = show
        self.update = True

    def show_faces(self, show = True):
        self._show_faces = show
        self.update = True



if __name__ == "__main__":
    i = Interface()
    i.start()

