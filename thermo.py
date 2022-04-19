import numpy as np
import scipy.optimize

# Python version of the thermodynamic calculations in DALES


# constants as in DALES
tup     = 268.            # Temperature range over which mixed phase occurs (high)
tdn     = 253.            # Temperature range over which mixed phase occurs (low)
rd      = 287.04          # gas constant for dry air.
rv      = 461.5           # gas constant for water vapor.
cp      = 1004.           # specific heat at constant pressure (dry air).
rlv     = 2.53e6          # latent heat for vaporisation
pref0   = 1.e5            # standard pressure used in exner function.
grav    = 9.81            # gravity acceleration.

# Saturation water pressure over liquid and ice
# as in DALES and 
#     D. M. Murphy and T. Koop 2005, "Review of the vapour
#     pressures of ice and supercooled water for atmospheric
#     applications."  Q. J. R. Meteorol. Soc. 131:1539.

def esatl(T):
     return np.exp(54.842763-6763.22/T-4.21*np.log(T)+0.000367*T+
         np.tanh(0.0415*(T-218.8))*(53.878-1331.22/T-9.44523*np.log(T)+ 0.014025*T))

def esati(T):
    return np.exp(9.550426-5723.265/T+3.53068*np.log(T)-0.00728332*T)

# ice - liquid ratio as function of temperature
# 1 for all liquid, 0 for all ice
def ilratio(T):
    return np.maximum(0.,np.minimum(1.,(T-tdn)/(tup-tdn)))

# exner function of pressure
def exnf(pres):
    return (pres/pref0)**(rd/cp)

# saturation humidity as in DALES
# linear interpolation between qsatur over liquid and qsatur over ice
#
# note IFS makes a different choice - linear interpolation vapor pressure
def qsatur(T, pres):
    esl1 = esatl(T)
    esi1 = esati(T)

    # this breaks if vapor pressure > real pressure
    # i.e. above boiling point of water at current pressure
    # original:
#    qsatur = (ilratio(T)     *(rd/rv)*esl1 / (pres - (1.-rd/rv)*esl1) +
#              (1.-ilratio(T))*(rd/rv)*esi1 / (pres - (1.-rd/rv)*esi1) )
    # with clamp
    qsat  = (ilratio(T)     *(rd/rv)*esl1 / (pres - np.minimum( (1.-rd/rv)*esl1, pres*0.8) ) +
              (1.-ilratio(T))*(rd/rv)*esi1 / (pres - np.minimum( (1.-rd/rv)*esi1, pres*0.8) ) )

    
    return np.clip(qsat, 0, 0.9)

# get (T, ql) from (thl, qt) at pressure pres
# accepts scalars or numpy arrays
def T_and_ql(thl, qt, pres):
    
    T = exnf(pres) * thl # first guess
    qsat = qsatur(T, pres)

#    if (qt < qsat):  # early return if below saturation
#        return T, 0  # doesn't work with vectors (could use .all for speed)
#                     # not needed for correctness
#    else:            # above saturation

# find T, ql such that ...
#   ql = max(qt - qsatur, 0.)
#   thl = T/exnf(pres) - (rlv/(cp*exnf(pres))) * ql

    def thl_err(t):
        ql = np.maximum(qt - qsatur(t, pres), 0.)
        thl1 = t/exnf(pres) - (rlv/(cp*exnf(pres))) * ql
        return thl - thl1

    def thl_err_scalar(t, qt, pres, thl):
        ql = np.maximum(qt - qsatur(t, pres), 0.)
        thl1 = t/exnf(pres) - (rlv/(cp*exnf(pres))) * ql
        return thl - thl1

    # T = scipy.optimize.broyden1(thl_err, T, f_tol=1e-5)
    #print(thl_err(200), thl_err(330))
    try:
        T = np.zeros_like(thl)
        for i in range(len(thl)):
            T[i] = scipy.optimize.brentq(thl_err_scalar, 200, 330, xtol=1e-3, args = (qt[i], pres[i], thl[i]))
    except:
        print('scalar version')
        T = scipy.optimize.brentq(thl_err_scalar, 200, 330, xtol=1e-3, args = (qt, pres, thl))
        
    ql = np.maximum(qt - qsatur(T, pres), 0.)
    return T, ql


# base pressure profile, for the option  ibas_prf=3
# "use standard atmospheric lapse rate with surface temperature offset"
# for now this version is valid only below 11 km
def pressure(zf, ps=101300, thls=300):
    # zmat=(/11000.,20000.,32000.,47000./)           # heights of lapse rate table
    lapserate=[-6.5/1000., 0., 1./1000, 2.8/1000 ]   # lapse rate table
        
    tsurf=thls*(ps/pref0)**(rd/cp) # surface temperature
    zsurf = 0
    #pmat = np.exp((log(ps)*lapserate(1)*rd+np.log(tsurf+zsurf*lapserate(1))*grav-
    #               np.log(tsurf+zmat(1)*lapserate(1))*grav)/(lapserate(1)*rd))

    pb = np.exp((np.log(ps)*lapserate[0]*rd + np.log(tsurf+zsurf*lapserate[0])*grav-
                 np.log(tsurf+zf*lapserate[0])*grav)/(lapserate[0]*rd))
    
    tb = tsurf+lapserate[0]*(zf - zsurf)

    rhobf = pb / (rd*tb) # dry estimate

    return pb
    
if __name__ == '__main__':
    p = np.array((101300, 90300))
    thl = np.array((300.0, 290.0))
    qt = np.array((0.025, 0.009))

    #p = 101300
    #thl = 300
    #qt = 0.025
    
    T, ql = T_and_ql(thl, qt, p)
    print(f'thl: {thl}  qt: {qt}  T:{T}  ql:{ql}  p:{p}')
    qsat = qsatur(T, p)
    print(f'qsatur({T}, p) : {qsat}' )
    print(f'qt-qsat: {qt - qsat}' )
    ql_test = np.maximum(qt - qsat, 0.)
    print (f'ql - ql_test : {ql - ql_test}')
    

    import matplotlib.pyplot as plt
    z = np.arange(1,7000, 100)
    p = pressure(z, thls=300, ps=101300)
    plt.plot(p, z)
    plt.show()
