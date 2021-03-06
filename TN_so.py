"""
Split operator module for two-phase flow
"""
#from __future__ import absolute_import

#from builtins import range
import os
from proteus.default_so import *
from proteus import Context
#from importlib import import_module
import TN

# Create context from main module
name_so = os.path.basename(__file__)
if '_so.py' in name_so[-6:]:
    name = name_so[:-6]
elif '_so.pyc' in name_so[-7:]:
    name = name_so[:-7]
else:
    raise NameError('Split operator module must end with "_so.py"')

case = __import__(name)
Context.setFromModule(case)
ct = Context.get()

# List of p/n files
pnList = []

# moving mesh
if ct.movingDomain:
    pnList += [("moveMesh_p", "moveMesh_n")]
    modelSpinUpList = [0]

# Navier-Stokes and VOF
pnList += [("twp_navier_stokes_p", "twp_navier_stokes_n"),
           ("vof_p", "vof_n")]

# Level set
if not ct.useOnlyVF:
    pnList += [("ls_p", "ls_n"),
               ("redist_p", "redist_n"),
               ("ls_consrv_p", "ls_consrv_n")]

# added mass
if ct.addedMass:
    pnList += [("added_mass_p","added_mass_n")]

if ct.useRANS > 0:
    pnList += [("kappa_p", "kappa_n"),
               ("dissipation_p", "dissipation_n")]

#systemStepControllerType = ISO_fixed_MinAdaptiveModelStep
if ct.dt_fixed:
#    systemStepControllerType = Sequential_FixedStep
    systemStepControllerType = Sequential_MinAdaptiveModelStep
    dt_system_fixed = ct.dt_fixed
    stepExactSystem=False
else:  # use CFL
    systemStepControllerType = Sequential_MinAdaptiveModelStep
    stepExactSystem=False

needEBQ_GLOBAL = False
needEBQ = False

modelSpinUpList = [0]  # for initial conditions of movemesh

if ct.opts.nsave == 0:
    if ct.dt_fixed > 0:
        archiveFlag = ArchiveFlags.EVERY_USER_STEP
        if ct.opts.dt_init < ct.dt_fixed:
            tnList = [0., ct.opts.dt_init, ct.dt_fixed, ct.opts.T]
        else:
            tnList = [0., ct.dt_fixed, ct.opts.T]
    else:
          tnList = [0., ct.opts.dt_init, ct.opts.T]
else:
    tnList=[0.0,ct.opts.dt_init]+[ct.opts.dt_init+ i*ct.dt_out for i in range(1,ct.nDTout+1)]

