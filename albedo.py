#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg') # to work without X

import os
import sys
#from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
from netCDF4 import Dataset, num2date, date2index # pip install netCDF4

from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

params = {
#"figure.figsize" :  [3.36, 2.976],  # figure size in inches
#                       "figure.dpi"     :  300,       # figure dots per inch
#                       "font.size"      :  8,       # this one acutally changes tick labels
#                       "font.family"    : "Times New Roman",
#                      'svg.fonttype'    : 'none',  # plot text as text - not paths or clones or other nonsense
#                       "legend.fontsize": "large",   # these don't seem to do anything for the tick label font size
#                       "axes.titlesize" : "large",
#                       "xtick.labelsize": "large",
                       "ytick.labelsize": 20, # for colorbar ticks
                       "axes.labelsize" : 20, # for colorbar labels
}

plt.rcParams.update(params)


ti = 0
lwpmax = 1
rwpmax = 1

#qrmax = qr.max()                       # qr -2.3676447e-22 0.008596641
#thlmin,thlmax = thl.min(), thl.max()   # thl 293.08685 297.84753

#print ('thl', thlmin, thlmax)
#print ('qr', qrmin, qrmax)

color1 ='#0080ff00' # transparent cyan
color2 ='#0080ffff' # solid cyan
color1b='#ffffff' # solid white 

cmap_rain = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

def albedo(lwp, Nc=70000000):
    # Albedo using model from Zhang et al. (2005)
    tau = 0.19 * lwp**(5./6) * Nc**(1.0/3)
    alb = tau/(6.8 + tau)
    return alb

def setup(rundir, size=None):
    crossxy_file=os.path.join(rundir, 'cape.nc')
    data = Dataset(crossxy_file, "r")

    #thl = data['/thlxy'][:,:,:] # seems to load all data now
    #qr  = data['/qrxy'][:,:,:]
    time = data['/time']
    lwp = data['/lwp']
    rwp = data['/rwp']
    
    #fig = plt.figure(figsize=(18, 13.5), dpi=80) # 1440 x 1080
    if size is None:
        size = 1080
    dpi = 80
    fig = plt.figure(figsize=(size/dpi, size/dpi), dpi=dpi)

    a = albedo(lwp[ti,:,:])
    imlwp = plt.imshow(a,           cmap='Greys_r', vmin=0, vmax=lwpmax)
    imrwp = plt.imshow(rwp[ti,:,:], cmap=cmap_rain, vmin=0, vmax=rwpmax)

    plt.axis('off')
    plt.gca().set_position([0, 0, 1, 1])

    # plt.gca().set_position([0, 0, .75, 1])
    # # colorbar for thl
    # cax = fig.add_axes([.8, 0.55, 0.03, .4])
    # cb = fig.colorbar(imthl, cax=cax)
    # cb.set_label(r'$\theta_l$ (K)')
    # # colorbar for qr
    # cax = fig.add_axes([.8, 0.05, 0.03, .4])
    # #cb = fig.colorbar(imqr, cax=cax)
    # #transparent colors in colormap gives stripes in the colorbar due to overlap.
    # cmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2b',[color1b,color2],256)
    # norm = mpl.colors.Normalize(vmin=qrmin, vmax=qrmax)
    # cb   = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)
    # cb.set_label(r'$q_r$ (g/kg)')
    # cb.locator = ticker.LinearLocator(6)
    # cb.update_ticks()


    timetext= plt.text(.98, .05, "",
                       horizontalalignment='right',
                       #verticalalignment='center',
                       #transform=fig.gca().transAxes,
                       transform=plt.gcf().transFigure,
                       color='Blue',
                       size=20)
    return lwp, rwp, time, fig, imlwp, imrwp, timetext

def select_time(lwp, rwp, time, fig, imlwp, imrwp, timetext, ti, run=''):
    #imlwp.set_data(lwp[ti,:,:])
    imlwp.set_data(albedo(lwp[ti,:,:]))
    imrwp.set_data(rwp[ti,:,:])

    hours=time[ti]/3600
    #t = "%2d days, %2.0f h"%(int(hours/24), int(hours%24))
    t = "%3.0f h"%(hours)
    if run:  #if run given, print just the run in the image
        t = run 
    timetext.set_text(t)


    
#for ti in range(100,103):
#    print(ti)
#    select_time(ti)
#    plt.savefig('frames/thl%04d.png'%ti)

# find time index of the time closest to t
def find_time_index(times, t):
    ti = np.abs((times[:]-t)).argmin()
    return ti

# times is a list of time points to plot, in hours
def plot_albedo(rundir, outdir, run=None, times=[24], size=None, filename=None):
    lwp, rwp, time, fig, imlwp, imrwp, timetext = setup(rundir, size)
    for t in times:
        t_sec = t*3600
        ti = find_time_index(time, t_sec)
        if np.abs(time[ti]-t_sec) < 600:
            select_time(lwp, rwp, time, fig, imlwp, imrwp, timetext, ti, run)
            if not filename:
                f='albedo%02d.png'%t
            else:
                f=filename
            if run:
                f = run + '_' + f
            outfile=os.path.join(outdir, f)
            plt.savefig(outfile)

    
def movie(rundir, outdir, run=''):
    lwp, rwp, time, fig, imlwp, imrwp, timetext = setup(rundir)

    nframes = time.shape[0]
    fps = 24
    duration= nframes/fps

    def make_frame(t):
        nonlocal fps, lwp, rwp, time, fig, imlwp, imrwp, timetext
        ti = int(t*fps)
        select_time(lwp, rwp, time, fig, imlwp, imrwp, timetext, ti)
        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=duration)
    outfile=os.path.join(outdir, 'albedo.mp4')
    animation.write_videofile(outfile, fps=fps)
 
