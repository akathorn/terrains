#!/usr/bin/bash
avconv -f image2 -r 25 -i video/%04d.jpeg -r 60 out.mp4
