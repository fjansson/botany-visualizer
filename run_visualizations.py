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


    # create visualizations directory in run dir
    outdir = os.path.join(r, 'visualizations')
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    #HEEPS plot settings:
    #colorbar = True
    #time_fmt = 'hms'
    #plot_times = [36]

    #Botany overview settings
    colorbar = False
    time_fmt = 'h'
    plot_times = [24 48 72 96]

    
    coldpool_viz = coldpool.Coldpool(rundir=r, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    coldpool_viz.plot(times=plot_times)
    coldpool_viz.movie()

    albedo_viz = albedo.Albedo(rundir=r, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    albedo_viz.plot(times=plot_times)
    albedo_viz.movie()

    thumbnail_viz = albedo.Albedo(rundir=r, outdir=thumbnail_dir, colorbar=False, time_fmt=None, size=160)
    thumbnail_viz.plot(times=[48], filename='thumbnail.png')


    twp_viz = twp.TWP(rundir=r, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    twp_viz.plot(times=plot_times)
    twp_viz.movie()
    #except:
    # pass
        # to handle broken runs / missing input files
        # also catches control-C - annoying


        

    
