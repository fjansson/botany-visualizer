#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg') # to work without X

import os
import sys
#from PIL import Image, ImageDraw, ImageFont
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
from netCDF4 import Dataset, num2date, date2index # pip install netCDF4

from plot import Plot

class Flux(Plot):
    def __init__(self, dales, data, outdir=None, size=1080, colorbar=False, time_fmt=None, dx=0, dy=0):
        super().__init__(data, outdir, size, colorbar, time_fmt)

        color1 ='#0080ff00' # transparent cyan
        color2 ='#0080ffff' # solid cyan
        color1b='#ffffff' # solid white
        self.moviename = 'flux.mp4'        
        self.plotname = 'flux'
        self.dales = dales
        
        cmap = 'bwr' # mpl.colors.LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

        
        ti = 0

        flux = np.copy(self.data.thl[ti,:,:]) # placeholder data of right size
        self.imflux = plt.imshow(flux, cmap=cmap, vmin=-.1, vmax=.1)

        
        if not self.colorbar:
            plt.gca().set_position([0, 0, 1, 1])
        else:
            plt.gca().set_position([0, 0, .75, 1])
            cax = self.fig.add_axes([.8, 0.55, 0.03, .4])
            cb = self.fig.colorbar(self.imflux, cax=cax)
            cb.set_label(r'Flux')
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

        qt = self.data.qt[ti,:,:]
        thl = self.data.thl[ti,:,:]  # qt, thl on a full level
        w = self.data.w[ti,:,:]      # inconsistency: w is on a half level

        thl_av = np.mean(thl)                                                                                     
        thlv = thl + 0.608*thl_av*qt

        thl = thl - thl_av
        thlv = thlv - np.mean(thlv)
        qt = qt - np.mean(qt)
        
        wthlv = w * thlv
        wthlv_av = np.mean(wthlv)

        # low-pass filter. Gaussian, with periodic boundary conditions.
        length = 5000 # 5 km length scale
        dx = self.dales.dx
        sigma = length / dx
        wthlv_f = sp.ndimage.gaussian_filter(wthlv, sigma, mode='wrap', truncate=3)  
        flux = wthlv_f - wthlv_av # low-pass-filtered flux anomaly from mean
        
    

        if vx or vy:
            dx = vx*ti
            dy = vy*ti
            flux = np.roll(flux, (-dy, -dx), (0,1))            

        self.imflux.set_data(flux)

        txt = self.format_time(self.data.time[ti])
        if run:  #if run given, print just the run in the image
            txt = run
        if self.text: # if the explicit text is given, print that
            txt = text
        self.timetext.set_text(txt)


