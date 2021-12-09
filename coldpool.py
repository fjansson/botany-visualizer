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

qrmin = 0    * 1000
qrmax = 0.01 * 1000 # *1000 for scaling to g/kg
thlmin = 293.0
thlmax = 298.0
#qrmax = qr.max()                       # qr -2.3676447e-22 0.008596641
#thlmin,thlmax = thl.min(), thl.max()   # thl 293.08685 297.84753

print ('thl', thlmin, thlmax)
print ('qr', qrmin, qrmax)

color1 ='#ff000000' # transparent red
color2 ='#ff0000ff' # solid red
color1b='#ffffff' # solid white 

cmap_rain = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

def setup(rundir):
    crossxy_file=os.path.join(rundir, 'crossxy.0001.nc')
    data = Dataset(crossxy_file, "r")

    #thl = data['/thlxy'][:,:,:] # seems to load all data now
    #qr  = data['/qrxy'][:,:,:]
    time = data['/time']
    thl = data['/thlxy']         # doesn't load everything
    qr  = data['/qrxy']

    #fig = plt.figure(figsize=(18, 13.5), dpi=80) # 1440 x 1080
    fig = plt.figure(figsize=(13.5, 13.5), dpi=80) # 1080 x 1080

    imthl = plt.imshow(thl[ti,:,:], vmin=thlmin, vmax=thlmax)
    imqr = plt.imshow(1000*qr[ti,:,:], cmap=cmap_rain, vmin=qrmin, vmax=qrmax)

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
                       size=20)
    return thl, qr, time, fig, imthl, imqr, timetext

def select_time(thl, qr, time, fig, imthl, imqr, timetext, ti):
    imthl.set_data(thl[ti,:,:])
    imqr.set_data(1000*qr[ti,:,:])

    hours=time[ti]/3600
    # t = "%2d days, %2.0f h"%(int(hours/24), int(hours%24))
    t = "%3.0f h"%(hours)
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
def plot_coldpool(rundir, outdir, run='', times=[24]):
    thl, qr, time, fig, imthl, imqr, timetext = setup(rundir)
    for t in times:
        t_sec = t*3600
        ti = find_time_index(time, t_sec)
        if np.abs(time[ti]-t_sec) < 600:
            select_time(thl, qr, time, fig, imthl, imqr, timetext, ti)
            outfile=os.path.join(outdir, 'coldpool%02d.png'%t)
            plt.savefig(outfile)

    
def movie(rundir, outdir, run=''):
    thl, qr, time, fig, imthl, imqr, timetext = setup(rundir)

    nframes = time.shape[0]
    fps = 24
    duration= nframes/fps

    def make_frame(t):
        nonlocal fps, thl, qr, time, fig, imthl, imqr, timetext
        ti = int(t*fps)
        select_time(thl, qr, time, fig, imthl, imqr, timetext, ti)
        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=duration)
    outfile=os.path.join(outdir, 'coldpool.mp4')
    animation.write_videofile(outfile, fps=fps)
 
