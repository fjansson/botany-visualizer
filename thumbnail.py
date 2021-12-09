#!/usr/bin/env python3

import os
import sys
from PIL import Image, ImageDraw, ImageFont

width = 160
height = 160

textpos = (10,height-24)
textcolor = (100,100,0)

        
font = ImageFont.load("10x20.pil")
#font = ImageFont.truetype("/home/pi/kanji/fonts/noto/NotoSansCJKjp-Medium.otf", display_size)

# extract name of the directory containing the run
# run = os.path.basename(os.path.abspath(run_path))
#
# if run is given it is used as the name of the run, as a prefix
# for the file name and overlaid on the image
def make_thumbnail(rundir, outdir, run=''):

    im = Image.new('RGB', (width, height) , color=(20,20,20))
    draw = ImageDraw.Draw(im)
    draw.text(textpos, run, textcolor, font=font)

    if run:
        imagename = f'{run}_thumbnail.png'
    else: 
        imagename = 'thumbnail.png'
        
    im.save(os.path.join(outdir, imagename))


