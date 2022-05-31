import matplotlib
matplotlib.use('Agg') # to work without X
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

import thermo

units = {
    'thl': 'K',
    'T'  : 'K',
    'qt' : 'g/kg',
    'ql' : 'g/kg',
    'u' : 'm/s',
    'w_ls' : 'cm/s',
    'RH' : '%',
    'tau' : 's',
}
scale = {
    'qt'   : 1000,
    'ql'   : 1000,
    'w_ls' : 100,
}

def plot_initial(d, outdir='./'):
    fig, axes = plt.subplots(nrows=1, ncols=8, sharey=True, squeeze=False)
    r=0
    axes[r,0].plot(d.init.thl, d.init.z) 
    axes[r,0].set(xlabel=f'thl ({units["thl"]})')
    axes[r,0].tick_params(axis='y', labelsize=8)
    axes[r,0].yaxis.label.set_fontsize(10)
    
    axes[r,1].plot(d.init.qt*scale.get('qt',1), d.init.z) 
    axes[r,1].set(xlabel=f'qt ({units["qt"]})')

    axes[r,2].plot(d.init.ql*scale.get('ql',1), d.init.z) 
    axes[r,2].set(xlabel=f'ql ({units["ql"]})')
    axes[r,2].set_xlim(left=0, right=0.0015*scale.get('ql',1))

    axes[r,3].plot(d.init.RH, d.init.z) 
    axes[r,3].set(xlabel=f'RH ({units["RH"]})')
    axes[r,3].set_xlim(left=0, right=150)
    
    axes[r,4].plot(d.init.T, d.init.z) 
    axes[r,4].set(xlabel=f'T ({units["T"]})')
    
    axes[r,5].plot(d.init.u, d.init.z)
    axes[r,5].set(xlabel=f'u ({units["u"]})')
    
    axes[r,6].plot(d.init.lw*scale.get('w_ls',1), d.init.z)
    axes[r,6].set(xlabel=r'$w_{ls}$ ' + f'({units["w_ls"]})')

    for ax in axes[r,:]:
        ax.xaxis.label.set_fontsize(10)
        ax.tick_params(axis='x', labelsize=8)

        
    if d.init.tau is not None:
        axes[r,7].semilogx(d.init.tau, d.init.z)
        axes[r,7].set(xlabel=r'$\tau_{nudge}$' +f'({units["tau"]})')
        
    plt.ylim(0, 7000)

    descr = '' # 'intr.rad. '+['off', 'on'][r]
    axes[r,0].set(ylabel=f'z (m)  {descr}')

    plt.subplots_adjust(left=.1, top=.99, bottom=.08, right=.99,
                        wspace=.2, hspace=.15)
    
    plt.savefig(os.path.join(outdir, 'profiles-initial.png'))


# find time index of the time closest to t
def find_time_index(times, t):
    ti = np.abs((times[:]-t)).argmin()
    return ti

def plot_profile(prof, dales, outdir='./', times=[12]):
    fig, axes = plt.subplots(figsize=(8,4), nrows=1, ncols=7, sharey=True, squeeze=False)

    r=0
    axes[r,0].tick_params(axis='y', labelsize=8)
    axes[r,0].yaxis.label.set_fontsize(10)
    for ax in axes[r,:]:
        ax.xaxis.label.set_fontsize(10)
        ax.tick_params(axis='x', labelsize=8)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

    cmap = plt.get_cmap('cool')

    z   = prof.zt[:]
    lw  = dales.init.lw
    pres = thermo.pressure(z, dales.ps, dales.thls)
    thl = dales.init.thl
    qt = dales.init.qt
    T,ql_ = thermo.T_and_ql(thl, qt, pres)
    qsat = thermo.qsatur(T, pres)
    RH = 100 * qt / qsat  # clamp to 100% or not?

    z /= 1000
    
    # initial profiles
    c='k'
    axes[r,0].plot(dales.init.thl, z, c=c)
    axes[r,1].plot(dales.init.qt*scale.get('qt',1), z, c=c)
    axes[r,2].plot(dales.init.ql*scale.get('ql',1), z, c=c)
    axes[r,3].plot(RH, z, c=c)
    axes[r,4].plot(T, z, c=c)
    axes[r,5].plot(dales.init.u, z, c=c)
    axes[r,6].plot(lw*scale.get('w_ls',1), z, c=c, label='initial')
        
    for t in times:
        c = cmap(t/times[-1])
        
        t_sec = t*3600
        ti = find_time_index(prof.time, t_sec)
        if np.abs(prof.time[ti]-t_sec) < 600:            
            u   = prof.u[ti][:]
            thl = prof.thl[ti][:]
            qt  = prof.qt[ti][:]
            ql  = prof.ql[ti][:]
            time= prof.time[ti]
            T,ql_ = thermo.T_and_ql(thl, qt, pres)
            qsat = thermo.qsatur(T, pres)
            RH = 100 * qt / qsat  # clamp to 100% or not?
            
            line, = axes[r,0].plot(thl, z, c=c)
            axes[r,0].set(xlabel=f'thl ({units["thl"]})')
            axes[r,0].set_xlim(left=295, right=340)
            
            line, = axes[r,1].plot(qt*scale['qt'], z, c=c)
            axes[r,1].set(xlabel=f'qt ({units["qt"]})')
            axes[r,1].set_xlim(left=0, right=17)
            
            line, = axes[r,2].plot(ql*scale['ql'], z, c=c)
            axes[r,2].set(xlabel=f'ql ({units["ql"]})')
            axes[r,2].set_xlim(left=0, right=.04)
        
            line, = axes[r,3].plot(RH, z, c=c)
            axes[r,3].set(xlabel=f'RH ({units["RH"]})')
            axes[r,3].set_xlim(left=0, right=120)
            
            line, = axes[r,4].plot(T, z, c=c)
            axes[r,4].set(xlabel=f'T ({units["T"]})')
            
            line, = axes[r,5].plot(u, z, c=c)
            axes[r,5].set(xlabel=f'u ({units["u"]})')

            l='%6.0fh'%(time/3600)                        
            line, = axes[r,6].plot(lw*scale['w_ls'], z, label=l, c=c)
            axes[r,6].set(xlabel=r'$w_{ls}$' + f'({units["w_ls"]})')
            
            
            plt.ylim(0, 7)

            descr = '' # 'intr.rad. '+['off', 'on'][r]
            axes[r,0].set(ylabel=f'z (km)  {descr}')

    filename='profiles.png'
    #plt.title('%6.2f h'%(time/3600))
    plt.subplots_adjust(left=.08, top=.98, bottom=.10, right=.99,
                        wspace=.1, hspace=.1)
    plt.legend()
    plt.savefig(os.path.join(outdir, filename))
    

def time_plot(tmser, cape, outdir='./'):
    fig, axes = plt.subplots(figsize=(8,6), nrows=4, ncols=1, sharex=True, squeeze=False)

    for ax in axes[:,0]:
        ax.xaxis.label.set_fontsize(10)
        ax.yaxis.label.set_fontsize(10)
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
    time = tmser.time[:] / 3600
    cfrac = np.maximum(tmser.cfrac[:], 0)
    axes[0,0].plot(time, cfrac, label='cfrac')
    #axes[0,0].set_ylim(bottom=0, top=1)
    axes[0,0].set(ylabel='cfrac')

    axes[1,0].plot(time, tmser.lwp_bar[:]*1000, label='LWP')
    axes[1,0].set(ylabel=r'LWP (g/m$^2$)')
    axes[2,0].plot(time, tmser.rwp_bar[:]*1000, label='LWP')
    axes[2,0].set(ylabel=r'RWP (g/m$^2$)')
    axes[3,0].plot(time, tmser.twp_bar[:], label='LWP')
    axes[3,0].set(ylabel=r'TWP (kg/m$^2$)')

    axes[3,0].set(xlabel='time (h)')

    # time = cape.time[:] / 3600
    # # save memory, don't load full lwp data at once
    # lwp = [np.mean(cape.lwp[i,:,:])*1000 for i in range(len(time))]
    # rwp = [np.mean(cape.rwp[i,:,:])*1000 for i in range(len(time))]
    # twp = [np.mean(cape.twp[i,:,:])      for i in range(len(time))]
    
    # axes[1,0].plot(time, lwp, label='LWP')
    # axes[1,0].set(ylabel='LWP (g/m$^2$)')
    # axes[2,0].plot(time, rwp, label='RWP')
    # axes[2,0].set(ylabel='RWP (g/m$^2$)')
    # axes[3,0].plot(time, twp, label='TWP')
    # axes[3,0].set(ylabel='TWP (kg/m$^2$)')
    

    
    
    filename='timeplot.png'
    plt.savefig(os.path.join(outdir, filename))

    
