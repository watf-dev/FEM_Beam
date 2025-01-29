#!/usr/bin/env python3
# Created: Nov, 05, 2024 15:10:16 by Wataru Fukuda

# DEBUG = True
DEBUG = False

import os
import numpy
from watfFEM.watfFEM import watfFEM
import watfio
import wataruel

### setting ###
DOF = 2  # degree of freedom
NEN = 4  # number of element nodes
NINT = 2  # number of integral points
SUPPORT_BOUNDARY = 1  ## todo: error with 2,3

## edit here ##
E = 4000000  # Young's modulus [kN/m^2]
NU = 0.3  # Poisson's ratio
PY = -1  ## any value except 1 [kN]

def main():
  import argparse
  parser = argparse.ArgumentParser(description="""\
  solving simple beam problem with FEM
""")
  parser.add_argument("config", help="Input configuration file")
  parser.add_argument("--output_dir", help="Output dir")
  parser.add_argument("--output_dis", help="Output file for displacement")
  parser.add_argument("--output_disx", help="Output file for X-displacement")
  parser.add_argument("--output_disy", help="Output file for Y-displacement")
  parser.add_argument("--output_nxx", help="Output file for normal stress in x")
  parser.add_argument("--output_nyy", help="Output file for normal stress in y")
  parser.add_argument("--output_nxy", help="Output file for shear stress")
  options = parser.parse_args()

  solver = watfFEM(options.config, DOF, NEN, NINT, SUPPORT_BOUNDARY, E, NU, PY)
  fixed_ien = solver.get_fixed_ien()
  fixed_u = solver.gen_fixed_u(fixed_ien)
  load_ien = solver.get_load_ien()
  K = solver.gen_K()
  U = solver.gen_U(fixed_u)
  F = solver.gen_F(fixed_u,load_ien)
  K,U,F = solver.deform_matrix(K,U,F)
  K1, K2, K3, K4, U_uk, U_k, F_k, F_uk = solver.split_matrix(K,U,F)
  U_uk = solver.calc_displacement(K1,K2,U_uk,U_k,F_k)
  U_uk = solver.fix_U_uk(U_uk,fixed_u)

  ### post processing
  dis_file = U_uk[:,1]
  nxx, nyy, nxy = solver.get_stress(dis_file)
  nxx = solver.ave_stress(nxx)
  nyy = solver.ave_stress(nyy)
  nxy = solver.ave_stress(nxy)

  if DEBUG:
    solver.print_debug(fixed_ien,fixed_u,load_ien,K)

  if options.output_dir:
    os.makedirs(options.output_dir,exist_ok=True)

  if options.output_dis:
    U_uk = numpy.array(U_uk[:,1],dtype=">f8")
    U_uk.tofile(os.path.join(options.output_dir,options.output_dis))
    print(f"Wrote to {options.output_dis}")
    if DEBUG:
      print("U_uk",U_uk)

  if options.output_disx:
    U_uk_x = numpy.array(U_uk[::2],dtype=">f8")
    U_uk_x.tofile(os.path.join(options.output_dir,options.output_disx))
    print(f"Wrote to {options.output_disx}")
    if DEBUG:
      print("U_uk_x",U_uk_x)

  if options.output_disy:
    U_uk_y = numpy.array(U_uk[1::2],dtype=">f8")
    U_uk_y.tofile(os.path.join(options.output_dir,options.output_disy))
    print(f"Wrote to {options.output_disy}")
    if DEBUG:
      print("U_uk_y",U_uk_y)

  if options.output_nxx:
    nxx = numpy.array(nxx, dtype=">f8")
    nxx.tofile(os.path.join(options.output_dir,options.output_nxx))
    print(f"Wrote to {options.output_nxx}")
    if DEBUG:
      print("nxx",nxx)

  if options.output_nyy:
    nyy = numpy.array(nyy, dtype=">f8")
    nyy.tofile(os.path.join(options.output_dir,options.output_nyy))
    print(f"Wrote to {options.output_nyy}")
    if DEBUG:
      print("nyy",nyy)

  if options.output_nxy:
    nxy = numpy.array(nxy, dtype=">f8")
    nxy.tofile(os.path.join(options.output_dir,options.output_nxy))
    print(f"Wrote to {options.output_nxy}")
    if DEBUG:
      print("nxy",nxy)


if(__name__ == '__main__'):
  main()

