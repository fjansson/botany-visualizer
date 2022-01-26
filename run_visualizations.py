#!/usr/bin/env python3

import thumbnail
import coldpool
import albedo
import twp
import glob
import os
import sys
from netCDF4 import Dataset

# open netcdf dataset(s), either from one single file or
# from files per variable
# dataset: 'cape', 'crossxy', 'fielddump'
class NC_loader:
    def __init__(self, path, dataset, level=1):
        self.path = path
        sources = {
            'cape'      : {'filename':'cape',                'fields':('lwp', 'rwp', 'twp', 'cldtop')},
            'crossxy'   : {'filename':f'crossxy.{level:04}', 'fields':('u', 'v', 'w', 'thl', 'qt', 'ql', 'qr')},
            'fielddump' : {'filename':'fielddump',           'fields':('u', 'v', 'w', 'thl', 'qt', 'ql', 'qr')},
        }

        rename_mapping = {'qr' : 'sv002',   # experimental remapping of variable names
                          'u'  : 'uxy',     # our name : variable name in input netcdf file
                          'v'  : 'vxy',
                          'w'  : 'wxy',
                          'thl': 'thlxy',
                          'qt' :'qtxy',
                          'ql' :'qlxy',
                          'qr' : 'qrxy',
                          }

        source = sources[dataset]
        filename = os.path.join(path, source['filename'])

        ds = None
        if os.path.exists(filename+'.nc'):
            ds = Dataset(filename+'.nc', "r")

        for field in source['fields']:
            if ds:
                ds_f = ds
            else:
                ds_f = Dataset(filename+'-'+field+'.nc', "r")
            varname = rename_mapping.get(field, field)
            setattr(self, field, ds_f[varname])

        self.time = ds_f['time'] # read time coordinate from the last file processed


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
    plot_times = [24, 48, 72, 96]

    cape  = NC_loader(r,'cape')
    crossxy = NC_loader(r,'crossxy', 1)

    coldpool_viz = coldpool.Coldpool(crossxy, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    coldpool_viz.plot(times=plot_times)
    coldpool_viz.movie()

    albedo_viz = albedo.Albedo(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    albedo_viz.plot(times=plot_times)
    albedo_viz.movie()

    thumbnail_viz = albedo.Albedo(cape, outdir=thumbnail_dir, colorbar=False, time_fmt=None, size=160)
    thumbnail_viz.plot(times=[48], filename='thumbnail.png')

    twp_viz = twp.TWP(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt)
    twp_viz.plot(times=plot_times)
    twp_viz.movie()
    #except:
    # pass
        # to handle broken runs / missing input files
        # also catches control-C - annoying
