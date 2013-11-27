Terrains

========

Applications of DeLaunay Triangulation and DCEL structure to digital terrain modelization.

========

Authors:
  Daniel Espino Timón       <s10m008@alumnos.fi.upm.es>
  Carlos García Huerta 	  	<s10m009@alumnos.fi.upm.es>
  Isaac Sánchez Ruiz			  <s10m024@alumnos.fi.upm.es>
  Marcos Sebastián Alarcón	<s10m026@alumnos.fi.upm.es>

Supervisor:
  Manuel Abellanas

========

Description:

  This project is the result of an assignment in the course Modelization, taught at
the computer science school in Universidad Politécnica de Madrid.

  The software can read ASCII files representing terrains provided by, for example,
the Spanish National Geographic Institute.

  Upon reading this file, a DCEL (doubly linked edge list) structure is created representing
a DeLaunay triangulation of the terrain. Partial implementation of river/mountain finding
algorithms is also provided.
  
========

Basic usage:

-Read .asc (ASCII) file
  ./main.py input.asc [proportion] [--3d]

  The second argument specifies a proportion of points to be randomly chosen from the file, ignoring the rest.
  The --3d argument can be used to obtain a 3d representation of the terrain.

-Load a .dcel file
  ./main.py entrada.dcel [--3d]


-Load and save a .dcel from the interactive shell
  >>> save(dcel, "./out.dcel")
  >>> load(dcel, "./in.dcel")
  
Some sample .asc and .dcel files are provided

