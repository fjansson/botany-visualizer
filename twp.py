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

from plot import Plot
    
class TWP(Plot):
    def __init__(self, data, outdir=None, size=1080, colorbar=False, time_fmt=None):
        super().__init__(data, outdir, size, colorbar, time_fmt)
        # TWP - deviation from frame mean

        
        #color1 ='#0080ff00' # transparent cyan
        #color2 ='#0080ffff' # solid cyan
        #color1b='#ffffff' # solid white

        #self.twpmin = 29 # range for total TWP
        #self.twpmax = 60
        self.twpmin = -2 # for TWP deviation from frame mean
        self.twpmax = 2
        self.moviename = 'twp.mp4'
        self.plotname = 'twp'
        #self.cmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

        #print('TWP range:', self.data.twp[:,:,:].min(), self.data.twp[:,:,:].max())

        ti = 0
        self.im = plt.imshow(self.data.twp[ti,:,:], vmin=self.twpmin, vmax=self.twpmax)
        # cmap='Greys_r'
        
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


    def select_time(self, ti, run='', vx=0, vy=0):
        twp = self.data.twp[ti,:,:]
        twp -= np.mean(twp)
        if vx or vy:
            dx = vx*ti
            dy = vy*ti
            twp = np.roll(twp, (-dy, -dx), (0,1))
        self.im.set_data(twp)

        txt = self.format_time(self.data.time[ti])
        if run:  #if run given, print just the run in the image
            txt = run
        self.timetext.set_text(txt)

