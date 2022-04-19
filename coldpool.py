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

qrmin = 0    * 1000
qrmax = 0.005 * 1000 # *1000 for scaling to g/kg
thlmin = 290.0
thlmax = 300.0

class Coldpool(Plot):
    def __init__(self, data, outdir=None, size=1080, colorbar=False, time_fmt=None):
        super().__init__(data, outdir, size, colorbar, time_fmt)
        
        color1 ='#ff000000' # transparent cyan
        color2 ='#ff0000ff' # solid cyan
        #color1b='#ffffff' # solid white
        self.moviename = 'coldpool.mp4'
        self.plotname = 'coldpool'

        self.cmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

        ti = 0
        self.imthl = plt.imshow(self.data.thl[ti,:,:], vmin=thlmin, vmax=thlmax)
        self.imqr = plt.imshow(1000*self.data.qr[ti,:,:], cmap=self.cmap, vmin=qrmin, vmax=qrmax)

        if not self.colorbar:
            plt.gca().set_position([0, 0, 1, 1])
        else:
            plt.gca().set_position([0, 0, .75, 1])
            cax = self.fig.add_axes([.8, 0.55, 0.03, .4])
            cb = self.fig.colorbar(self.imqr, cax=cax)
            cb.set_label(r'q$_r$ (g/kg)')
            cax = self.fig.add_axes([.8, 0.05, 0.03, .4])
            cb2 = self.fig.colorbar(self.imthl, cax=cax)
            cb2.set_label(r'$\theta_l$ (K)')

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
        thl = self.data.thl[ti,:,:]
        qr  = 1000*self.data.qr[ti,:,:]
        if vx or vy:
            dx = vx*ti
            dy = vy*ti
            thl = np.roll(thl, (-dy, -dx), (0,1))
            qr  = np.roll(qr,  (-dy, -dx), (0,1))
        self.imthl.set_data(thl)
        self.imqr.set_data(qr)

        txt = self.format_time(self.data.time[ti])
        if run:  #if run given, print just the run in the image
            txt = run
        self.timetext.set_text(txt)

