#!/usr/bin/env python3

import thumbnail
import coldpool
import albedo
import glob
import os


thumbnail_dir = '/home/hp200321/data/botany-6-768/thumbnails'
if not os.path.isdir(thumbnail_dir):
    os.makedirs(thumbnail_dir)

rundir = '/home/hp200321/data/botany-6-768/runs'

Runs = glob.glob(os.path.join(rundir, 'Run_*'))

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
    except:
        pass
        # to handle broken runs / missing input files
        # also catches control-C - annoying

    
