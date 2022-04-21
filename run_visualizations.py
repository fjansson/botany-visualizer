#!/usr/bin/env python3

import thumbnail
import coldpool
import albedo
import twp
import flux
import webpage
import profileplot
import thermo

import glob
import os
import sys
from netCDF4 import Dataset
import f90nml
import types
import numpy as np

class Dales_loader:
    def __init__(self, path, exp_nr='001'):
        try:
            self.name = path.split('/')[-1] # last part of path as run name
        except:
            self.name = 'run'

        name = os.path.join(path, f'namoptions.{exp_nr}')
        self.nml = f90nml.read(name)
        self.params = self.nml['VVUQ_extra'] # the parameters varied

        self.ps   = self.nml['PHYSICS']['ps']
        self.thls = self.nml['PHYSICS']['thls']

        prof = np.loadtxt(os.path.join(path,f'prof.inp.{exp_nr}'))
        lscale = np.loadtxt(os.path.join(path,f'lscale.inp.{exp_nr}'))

        self.init = types.SimpleNamespace()
        self.init.z = lscale[:,0]
        self.init.lw = lscale[:,3]
        self.init.thl = prof[:,1]
        self.init.qt  = prof[:,2]
        self.init.u   = prof[:,3]
        self.init.v   = prof[:,4]
        self.init.pres = thermo.pressure(self.init.z, self.ps, self.thls)
        self.init.T,self.init.ql = thermo.T_and_ql(self.init.thl, self.init.qt, self.init.pres)
        self.init.qsat = thermo.qsatur(self.init.T, self.init.pres)
        self.init.RH = 100 * self.init.qt / self.init.qsat  # clamp to 100% or not?
        try:
            nudge = np.loadtxt(os.path.join(d,'nudge.inp.001'),
                               skiprows=3, max_rows=len(z))
            self.init.tau = nudge[:,1] # nudging time
        except:
            nudge = None
            self.init.tau = None



# open netcdf dataset(s), either from one single file or
# from files per variable
# dataset: 'cape', 'crossxy', 'fielddump'
class NC_loader:
    def __init__(self, path, dataset, level=1, exp_nr='001'):
        self.path = path
        sources = {
            'cape'      : {'filename':'cape',     'fields':('lwp', 'rwp', 'twp', 'cldtop')},
            'crossxy'   : {'filename':f'crossxy', 'fields':('u', 'v', 'w', 'thl', 'qt', 'ql', 'qr')},
            'fielddump' : {'filename':'fielddump','fields':('u', 'v', 'w', 'thl', 'qt', 'ql', 'qr')},
            'profiles'  : {'filename':f'profiles.{exp_nr}', 'fields':('zt', 'u', 'v', 'thl', 'qt', 'ql')},
            'tmser'     : {'filename':f'tmser.{exp_nr}', 'fields':('cfrac', 'lwp_bar', 'zb', 'zi', 'zc_max')},
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

        if dataset=='crossxy':
            level=f'.{level:04}'
        else:
            level=''

        source = sources[dataset]
        filename = os.path.join(path, source['filename'])

        ds = None
        print ('looking for ' + filename+level+'.nc')
        if os.path.exists(filename+level+'.nc'):
            ds = Dataset(filename+level+'.nc', "r")

        for field in source['fields']:
            if ds:
                ds_f = ds
            else:
                print ('looking for ' + filename+'-'+field+level+'.nc')
                ds_f = Dataset(filename+'-'+field+level+'.nc', "r")
            if dataset == 'crossxy':
                varname = rename_mapping.get(field, field)
            else:
                varname = field
            setattr(self, field, ds_f[varname])

        self.time = ds_f['time'] # read time coordinate from the last file processed

        # get coordinate arrays from last file processed - they may not all exist
        for c in ['xt', 'yt', 'zt']:
            try:
                setattr(self, 'c', ds_f[c][:])
            except:
                setattr(self, 'c', None)



make_movie = False 

if len(sys.argv) > 1:
    experiment_dir = sys.argv[1]
else:
    print('usage example: run_visualizations.py /home/hp200321/data/botany-6-768/')
    sys.exit(1)

run_dir = os.path.join(experiment_dir, 'runs')
Runs = glob.glob(os.path.join(run_dir, '*un_*')) #match borth Run_NN and run_NN
thumbnail_dir = os.path.join(experiment_dir, 'thumbnails')

if len(Runs) == 0: # there are no Run_NN directories in experiment_dir, treat it as a single run to process
    Runs = [experiment_dir]
    thumbnail_dir = experiment_dir

if not os.path.isdir(thumbnail_dir):
    os.makedirs(thumbnail_dir)

visualization_dirs = [] # list of output directories, used for webpage
                        # to do: more structure, pass also run parameters
                        # to do: use relative paths
for r in Runs:
    try:
        run_name = r.split('un_')[1] # match run_NN or Run_NN
    except:
        run_name = ''
    print(r, run_name)

    dales = Dales_loader(r)

    #Thumbnail
    #thumbnail.make_thumbnail(rundir=r, outdir=thumbnail_dir, run=run_name)
    # placeholder thumbnail: albedo


    # create visualizations directory in run dir
    outdir = os.path.join(r, 'visualizations')

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    visualization_dirs.append((outdir, dales))

    #HEEPS plot settings:
    #colorbar = True
    #time_fmt = 'hms'
    #plot_times = [36]

    #Botany overview settings
    colorbar = False
    time_fmt = 'h'
    plot_times = [24, 48, 72, 96]

    try:
        cape      = NC_loader(r,'cape')
        crossxy   = NC_loader(r,'crossxy', 1)
        crossxy13 = NC_loader(r,'crossxy', 13)
        profiles  = NC_loader(r,'profiles')
        tmser     = NC_loader(r,'tmser')
    except:
        print("Failed to load netCDFs, continuing with other runs.")
        continue
        
    size = cape.lwp.shape[1] # number of cells in y
    movie_size = min(size, 1080)
    print(f'Still image size {size}')
    print(f'Movie size {movie_size}')

    vx=-60 # camera drift velocity in grid cells/frame
    vy=-10
    framerate=20

    profileplot.plot_initial(dales, outdir=outdir)
    profileplot.plot_profile(profiles, dales, outdir=outdir,
                             times=[12,24,36,48])
    profileplot.time_plot(tmser, cape, outdir=outdir)

    
    coldpool_viz = coldpool.Coldpool(crossxy, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=size)
    coldpool_viz.plot(times=plot_times)
    coldpool_viz = coldpool.Coldpool(crossxy, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=movie_size)
    if make_movie:
        coldpool_viz.movie(vx=vx, vy=vy, fps=framerate)

    albedo_viz = albedo.Albedo(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=size)
    albedo_viz.plot(times=plot_times)
    albedo_viz = albedo.Albedo(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=movie_size)
    if make_movie:
        albedo_viz.movie(vx=vx, vy=vy, fps=framerate)

    # bug: all runs written to the same name
    #thumbnail_viz = albedo.Albedo(cape, outdir=thumbnail_dir, colorbar=False, time_fmt=None, size=160)
    #thumbnail_viz.plot(times=[48], filename='thumbnail.png')

    # place another thumbnail in the output directory of this job
    thumbnail_viz = albedo.Albedo(cape, outdir=outdir, colorbar=False, time_fmt=None, size=160, text=run_name)
    thumbnail_viz.plot(times=[48], filename='thumbnail.png')

    twp_viz = twp.TWP(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=size)
    twp_viz.plot(times=plot_times)
    twp_viz = twp.TWP(cape, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=movie_size)
    if make_movie:
        twp_viz.movie(vx=vx, vy=vy, fps=framerate)

    flux_viz = flux.Flux(crossxy13, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=size)
    flux_viz.plot(times=plot_times)
    flux_viz = flux.Flux(crossxy13, outdir=outdir, colorbar=colorbar, time_fmt=time_fmt, size=movie_size)
    if make_movie:
        flux_viz.movie(vx=vx, vy=vy, fps=framerate)


    #except:
    # pass
        # to handle broken runs / missing input files
        # also catches control-C - annoying

webpage.index(experiment_dir, visualization_dirs)
