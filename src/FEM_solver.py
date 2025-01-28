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
NINT = 3  # number of integral points
SUPPORT_BOUNDARY = 1  ## todo: error with 2,3

## edit here ##
E = 1  # Young's modulus
NU = 0.2  # Poisson's ratio
PY = -10  ## any value except 1

def main():
  import argparse
  parser = argparse.ArgumentParser(description="""\
  solving simple beam problem with FEM
""")
  parser.add_argument("config", help="Input configuration file")
  parser.add_argument("-o", "--output", help="Output file")
  parser.add_argument("--output_x", help="Output file for X-displacement")
  parser.add_argument("--output_y", help="Output file for Y-displacement")
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

  if DEBUG:
    solver.print_debug(fixed_ien,fixed_u,load_ien,K)

  if options.output:
    U_uk = numpy.array(U_uk[:,1],dtype=">f8")
    U_uk.tofile(options.output)
    print(f"Wrote to {options.output}")
    if DEBUG:
      print("U_uk",U_uk)

  if options.output_x:
    U_uk_x = numpy.array(U_uk[::2],dtype=">f8")
    U_uk_x.tofile(options.output_x)
    print(f"Wrote to {options.output_x}")
    if DEBUG:
      print("U_uk_x",U_uk_x)

  if options.output_y:
    U_uk_y = numpy.array(U_uk[1::2],dtype=">f8")
    U_uk_y.tofile(options.output_y)
    print(f"Wrote to {options.output_y}")
    if DEBUG:
      print("U_uk_y",U_uk_y)


if(__name__ == '__main__'):
  main()

