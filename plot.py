#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg') # to work without X
import matplotlib.pyplot as plt
import numpy as np
import os

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

class Plot:
    def __init__(self, data, outdir=None, size=1080, colorbar=False, time_fmt=None, text=""):
        self.outdir = outdir
        self.colorbar = colorbar
        self.time_fmt = time_fmt
        self.data = data
        self.text = text # optional text instead of time stamp
        
        dpi = 80
        sizex = size
        if colorbar:
            sizex *= 4/3
        self.fig = plt.figure(figsize=(sizex/dpi, size/dpi), dpi=dpi)
        
        self.timetext = plt.text(.98, .98, "",  #y was 0.05
                                 horizontalalignment='right',
                                 verticalalignment='top',
                                 #transform=fig.gca().transAxes,
                                 transform=plt.gcf().transFigure,
                                 color='#ffbbcc',
                                 size=30)
        plt.axis('off')

    def format_time(self, t):
        hours = int(t/3600)
        minutes = int(t/60)%60
        seconds = int(t)%60
        if self.time_fmt == 'hms':
            return "%3.0f:%02d:%02d"%(hours,minutes,seconds)
        return "%3.0f h"%(hours)

    # times is a list of time points to plot, in hours
    def plot(self, times=[24], run=None, filename=None):
        for t in times:
            t_sec = t*3600
            ti = find_time_index(self.data.time, t_sec)
            if np.abs(self.data.time[ti]-t_sec) < 600:
                self.select_time(ti, run)
                if not filename:
                    f=self.plotname+'%02d.png'%t
                else:
                    f=filename
                if run:
                    f = run + '_' + f
                outfile=os.path.join(self.outdir, f)
                self.fig.savefig(outfile)


    def movie(self, fps=24, run='', vx=0, vy=0):
        nframes = self.data.time.shape[0]
        duration= nframes/fps

        def make_frame(t):
            nonlocal self, fps, run
            ti = int(t*fps+.5)
            self.select_time(ti, run, vx=vx, vy=vy)
            return mplfig_to_npimage(self.fig)

        animation = VideoClip(make_frame, duration=duration)
        outfile=os.path.join(self.outdir, self.moviename)
        animation.write_videofile(outfile, fps=fps)

