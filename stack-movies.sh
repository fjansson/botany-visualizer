#!/bin/bash

#start at 20h

#directory for input and output
d=$1

#seek to position $start in all input movies
start=00:00:09
FONT=DejaVuSansMono.ttf
fs=48

ffmpeg -ss $start -i $d/twp.mp4 \
       -ss $start -i $d/albedo.mp4 \
       -ss $start -i $d/coldpool.mp4 \
       -filter_complex "hstack=inputs=3 , \
       drawtext=text='TWP':              fontfile=$FONT:fontcolor=white: fontsize=$fs: x=w/6-(text_w)/2: y=40,  \
       drawtext=text='albedo, RWP':      fontfile=$FONT:fontcolor=white: fontsize=$fs: x=w/6+w/3-(text_w)/2: y=40,  \
       drawtext=text='surface thl, qr':  fontfile=$FONT:fontcolor=white: fontsize=$fs: x=w/6+2*w/3-(text_w)/2: y=40" \
       $d/combined.mp4
