#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, os, time, threading, random, traceback, readline
import code, readline, rlcompleter

from StringIO import StringIO

from display import display2d, display3d

from dcel import DCEL, load, save
from read_asc import parse
from utils import random_filter
from algoritmos import *

global interface, dcel


class App(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interactive = True

    def run(self):
        if ("--load" in sys.argv) or (sys.argv[1].endswith(".dcel")):
            print "Loading file"
            print "Las opciones que no sean de display serán ignoradas"
            load(dcel, sys.argv[1])
        #que pasa si load no puede leer?

        else:
            print "Parsing file"
            points = parse(sys.argv[1])
            print len(points), "points read"

            print "Filtering"
            prop = 1
            try:
                if len(sys.argv) > 2 and not option(sys.argv[2]):
                    prop = float(sys.argv[2])
            except ValueError:
                print "¿La probabilidad", sys.argv[2],"es un número?"
                sys.exit(1)

            filtered_points = random_filter(points, prop)
            print len(filtered_points), "points chosen"

            if "--shuffle" in sys.argv:
                random.shuffle(filtered_points)


            if "--auto-exit" in sys.argv:
                self.interactive = False


            generate_dcel(filtered_points, dcel)

        if self.interactive:
            launch_terminal(locals())


def generate_dcel(points, dcel):
    print "Generating dcel"

    dcel.initial_triangulation()
    dcel.add_points(points)

    print "Triangulating"

    dcel.remove_initial()

    #dcel.remove_initial()

def option(string):
    options = ["--disco", "--shuffle", "--auto-exit", "--3d", "--load",
               "--help"]
    return string in options

def launch_terminal(environment = {}):
    global interface
    readline.parse_and_bind("tab: complete")
    environment.update(globals())
    # sys.stdout = outbuff
    # sys.stderr = outbuff
    code.interact(">>>", raw_input, local = environment)
    sys.exit()


if __name__ == "__main__":


#    outbuff = StringIO()

    dcel = DCEL()

    if len(sys.argv) < 2:
        launch_terminal()


    if option(sys.argv[1]):
        if sys.argv[1] == "--help":
            print "Uso: %s fichero [proporcion [--help] [--3d] [--auto-exit] [--disco] [--load] [--shuffle]]" % sys.argv[0]
        else:
            print "El primer fichero tiene que ser un path"
        sys.exit(1)

    if len(sys.argv) > 3:
        for i in xrange(3,len(sys.argv)):
            if not option(sys.argv[i]):
                print "El argumento", sys.argv[i], "no es una opción válida"
                sys.exit(1)


    disco = False
    if "--disco" in sys.argv:
        disco = True

    if "--3d" in sys.argv:
        interface = display3d.Interface(dcel)#, inbuff = os.fdopen(0, 'w'),
#                                        outbuff = outbuff)
    else:
        interface = display2d.Interface(dcel, discoteca = disco)

    app = App()
    app.start()

    while interface.loop() and app.is_alive():
        pass

    app.join()
#    outbuff.close()
