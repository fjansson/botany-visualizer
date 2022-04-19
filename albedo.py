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

def albedo(lwp, Nc=70000000):
    # Albedo using model from Zhang et al. (2005)
    tau = 0.19 * lwp**(5./6) * Nc**(1.0/3)
    alb = tau/(6.8 + tau)
    return alb


class Albedo(Plot):
    def __init__(self, data, outdir=None, size=1080, colorbar=False, time_fmt=None, text=''):
        super().__init__(data, outdir, size, colorbar, time_fmt, text)
        
        self.lwpmax = 1
        self.rwpmax = 3

        self.moviename = 'albedo.mp4'
        self.plotname = 'albedo'
        
        color1 ='#0080ff00' # transparent cyan
        color2 ='#0080ffff' # solid cyan
        color1b='#ffffff' # solid white

        cmap = mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)


        ti = 0
        rwp = np.copy(self.data.rwp[ti,:,:])
        a = albedo(self.data.lwp[ti,:,:])

        self.imlwp = plt.imshow(a,   cmap='Greys_r', vmin=0, vmax=self.lwpmax)
        self.imrwp = plt.imshow(rwp, cmap=cmap, vmin=0, vmax=self.rwpmax)

        if not self.colorbar:
            plt.gca().set_position([0, 0, 1, 1])
        else:
            plt.gca().set_position([0, 0, .75, 1])
            cax = self.fig.add_axes([.8, 0.55, 0.03, .4])
            cb = self.fig.colorbar(self.imrwp, cax=cax)
            cb.set_label(r'RWP kg/m$^2$')
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
        """
        vx, vy: camera translation velocity in pixels/frame
        """
        rwp = np.copy(self.data.rwp[ti,:,:])
        a = albedo(self.data.lwp[ti,:,:])

        if vx or vy:
            dx = vx*ti
            dy = vy*ti
            rwp = np.roll(rwp, (-dy, -dx), (0,1))
            a   = np.roll(a,   (-dy, -dx), (0,1))

        self.imlwp.set_data(a)
        self.imrwp.set_data(rwp)

        txt = self.format_time(self.data.time[ti])
        if run:  #if run given, print just the run in the image
            txt = run
        if self.text: # if the explicit text is given, print that
            txt = self.text
        self.timetext.set_text(txt)

