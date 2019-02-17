"""
A set of tests for using the QCEngine project
"""

import copy
import numpy as np
import json, os, shutil
from . import addons
import geometric
import pytest
import itertools

localizer = addons.in_folder

pdb_water3 = """REMARK   1 CREATED WITH FORCEBALANCE 2019-02-17
HETATM    1  O   HOH A   1       0.856  -1.382   0.317  0.00  0.00           O  
HETATM    2  H1  HOH A   1       1.675  -1.848   0.486  0.00  0.00           H  
HETATM    3  H2  HOH A   1       1.118  -0.468   0.206  0.00  0.00           H  
TER
HETATM    4  O   HOH A   2      -1.099  -0.858   2.173  0.00  0.00           O  
HETATM    5  H1  HOH A   2      -0.403  -1.146   1.582  0.00  0.00           H  
HETATM    6  H2  HOH A   2      -1.085   0.097   2.113  0.00  0.00           H  
TER
HETATM    7  O   HOH A   3       1.864   1.220   1.333  0.00  0.00           O  
HETATM    8  H1  HOH A   3       2.010   1.883   0.658  0.00  0.00           H  
HETATM    9  H2  HOH A   3       2.642   0.663   1.295  0.00  0.00           H  
TER
"""

@addons.using_openmm
def test_rebuild_openmm_water3(localizer):
    with open('water3.pdb', 'w') as f:
        f.write(pdb_water3)
    progress = geometric.optimize.run_optimizer(openmm=True, pdb='water3.pdb', coordsys='dlc', input='tip3p.xml')
    # The results here are in Angstrom
    # 
    ref = np.array([[ 1.19172917, -1.71174316,  0.79961878],
                    [ 1.73335403, -2.33032763,  0.30714483],
                    [ 1.52818406, -0.83992919,  0.51498083],
                    [-0.31618326,  0.13417074,  2.15241103],
                    [ 0.07716192, -0.68377281,  1.79137674],
                    [-0.98942711, -0.18943265,  2.75288307],
                    [ 1.64949098,  0.96407596,  0.43451244],
                    [ 0.91641967,  0.91098247,  1.07801098],
                    [ 1.78727054,  1.90697627,  0.33206132]])
    e_ref = -0.0289248308
    xdiff = (progress.xyzs[-1] - ref).flatten()
    rmsd, maxd = geometric.optimize.calc_drms_dmax(progress.xyzs[-1], ref, align=True)
    print("RMS / Max displacement from reference:", rmsd, maxd)
    # This test is a bit stochastic and doesn't converge to the same minimized geometry every time.
    # Check that the energy is 0.01 a.u. above reference. Not really the qm_energy, this is a misnomer
    assert progress.qm_energies[-1] < (e_ref + 0.01)
    # Check that the optimization converged in less than 200 steps
    assert len(progress) < 200
    # Check that the geometry matches the reference to within 0.03 RMS 0.05 max displacement
    assert rmsd < 0.03
    assert maxd < 0.05


