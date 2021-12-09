#!/usr/bin/env python3

import thumbnail
import coldpool
import albedo
import twp
import glob
import os
import sys

if len(sys.argv) > 1:
    experiment_dir = sys.argv[1]
else:
    print('usage example: run_visualizations.py /home/hp200321/data/botany-6-768/')
    sys.exit(1)
    
run_dir = os.path.join(experiment_dir, 'runs')
thumbnail_dir = os.path.join(experiment_dir, 'thumbnails')

if not os.path.isdir(thumbnail_dir):
    os.makedirs(thumbnail_dir)

Runs = glob.glob(os.path.join(run_dir, 'Run_*'))

for r in Runs:
    try:
        run_name = r.split('Run_')[1]
    except:
        run_name = ''
    print(r, run_name)

    #Thumbnail
    #thumbnail.make_thumbnail(rundir=r, outdir=thumbnail_dir, run=run_name)
    # placeholder thumbnail: albedo
    try:
        albedo.plot_albedo(rundir=r, outdir=thumbnail_dir, run=run_name, times=[48], size=160, filename='thumbnail.png')

        # create visualizations directory in run dir
        outdir = os.path.join(r, 'visualizations')
        if not os.path.isdir(outdir):
            os.makedirs(outdir)

        coldpool.plot_coldpool(rundir=r, outdir=outdir, times=[24,48,72])
        coldpool.movie(rundir=r, outdir=outdir)
        albedo.plot_albedo(rundir=r, outdir=outdir, times=[24,48,72])
        albedo.movie(rundir=r, outdir=outdir)

        twp_viz = twp.TWP(rundir=r, outdir=outdir)
        twp_viz.plot(times=[24,48,72])
        twp_viz.movie()
    except:
        pass
        # to handle broken runs / missing input files
        # also catches control-C - annoying


        

    
