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

# find time index of the time closest to t
def find_time_index(times, t):
    ti = np.abs((times[:]-t)).argmin()
    return ti

class TWP:
    def __init__(self, data, outdir=None, size=1080, colorbar=False, time_fmt=None):
        #color1 ='#0080ff00' # transparent cyan
        #color2 ='#0080ffff' # solid cyan
        #color1b='#ffffff' # solid white

        self.twpmin = 29
        self.twpmax = 60

        #self.cmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

        self.outdir = outdir
        self.colorbar = colorbar
        self.time_fmt = time_fmt
        self.data = data

        #print('TWP range:', self.data.twp[:,:,:].min(), self.data.twp[:,:,:].max())

        dpi = 80
        sizex = size
        if colorbar:
            sizex *= 4/3
        self.fig = plt.figure(figsize=(sizex/dpi, size/dpi), dpi=dpi)

        ti = 0
        self.im = plt.imshow(self.data.twp[ti,:,:], vmin=self.twpmin, vmax=self.twpmax)
        # cmap='Greys_r'

        plt.axis('off')


        self.timetext = plt.text(.98, .05, "",
                                 horizontalalignment='right',
                                 #verticalalignment='center',
                                 #transform=fig.gca().transAxes,
                                 transform=plt.gcf().transFigure,
                                 color='Blue',
                                 size=20)
        if not self.colorbar:
            plt.gca().set_position([0, 0, 1, 1])
        else:
            plt.gca().set_position([0, 0, .75, 1])
            cax = self.fig.add_axes([.8, 0.55, 0.03, .4])
            cb = self.fig.colorbar(self.im, cax=cax)
            cb.set_label(r'TWP kg/m$^2$')
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


    def format_time(self, t):
        hours = int(t/3600)
        minutes = int(t/60)%60
        seconds = int(t)%60
        if self.time_fmt == 'hms':
            return "%3.0f:%02d:%02d"%(hours,minutes,seconds)
        return "%3.0f h"%(hours)

    def select_time(self, ti, run=''):
        #imlwp.set_data(lwp[ti,:,:])
        self.im.set_data(self.data.twp[ti,:,:])

        txt = self.format_time(self.data.time[ti])
        if run:  #if run given, print just the run in the image
            txt = run
        self.timetext.set_text(txt)

    # times is a list of time points to plot, in hours
    def plot(self, times=[24], run=None, filename=None):
        for t in times:
            t_sec = t*3600
            ti = find_time_index(self.data.time, t_sec)
            if np.abs(self.data.time[ti]-t_sec) < 600:
                self.select_time(ti, run)
                if not filename:
                    f='twp%02d.png'%t
                else:
                    f=filename
                if run:
                    f = run + '_' + f
                outfile=os.path.join(self.outdir, f)
                self.fig.savefig(outfile)


    def movie(self, fps=24, run=''):
        nframes = self.data.time.shape[0]
        duration= nframes/fps

        def make_frame(t):
            nonlocal self, fps, run
            ti = int(t*fps+.5)
            self.select_time(ti, run)
            return mplfig_to_npimage(self.fig)

        animation = VideoClip(make_frame, duration=duration)
        outfile=os.path.join(self.outdir, 'twp.mp4')
        animation.write_videofile(outfile, fps=fps)
