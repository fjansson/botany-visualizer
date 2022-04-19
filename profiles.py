import matplotlib
matplotlib.use('Agg') # to work without X
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

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
