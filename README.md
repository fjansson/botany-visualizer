# DALES visualization scripts

A collection of scripts for automatically generating a set of plots and movies
for a set of DALES runs.

## Setup

### Anaconda on Fugaku

Set up anaconda as specified here:
https://github.com/dalesteam/dales/wiki/DALES-on-Fugaku

Then install additional packages:

```
conda install pillow
conda install -c conda-forge moviepy
```

### Alternative using pip

```
pip install matplotlib netcdf4 pillow moviepy f90nml
```

(not fully tested)

# Use

* merge the netcdf output tiles using `cdo`
* edit paths and settings in the top-leve script `run_visualizations.py`
* run the script `run_visualizations.py`

# To Do

* organization
* more plots
* parallelization
