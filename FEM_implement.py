#!/usr/bin/env python3
# Created: Nov, 05, 2024 15:10:16 by Wataru Fukuda

# DEBUG = True
DEBUG = False

import os
import numpy

### setting ###
dof = 2  # degree of freedom
nen = 4  # number of element nodes
nint = 3  # number of integral points
support_boundary = 1  ## todo: error with 2,3

## edit here ##
E = 1  # Young's modulus
nu = 0.2  # Poisson's ratio
Py = -10  ## any value except 1

def gen_H(xi,eta):
  H = numpy.zeros((dof,nen),dtype=">f8")
  H[0][0] = 1/4 * (1 - eta) * (-1)
  H[0][1] = 1/4 * (1 - eta)
  H[0][2] = 1/4 * (1 + eta) 
  H[0][3] = 1/4 * (1 + eta) * (-1)
  H[1][0] = 1/4 * (1 - xi) * (-1)
  H[1][1] = 1/4 * (1 + xi) * (-1)
  H[1][2] = 1/4 * (1 + xi)
  H[1][3] = 1/4 * (1 - xi)
  return H

def gen_J(xi,eta,xyz):
  H = gen_H(xi,eta)
  J = H@xyz
  return J

def gen_B(xi,eta,xyz):
  B = numpy.zeros((3,dof*nen),dtype=">f8")
  J = gen_J(xi,eta,xyz)
  J_inv = numpy.linalg.inv(J)
  H = gen_H(xi,eta)
  JH = J_inv@H
  B[0][0] = JH[0][0]
  B[0][2] = JH[0][1]
  B[0][4] = JH[0][2]
  B[0][6] = JH[0][3]
  B[1][1] = JH[1][0]
  B[1][3] = JH[1][1]
  B[1][5] = JH[1][2]
  B[1][7] = JH[1][3]
  B[2][0] = JH[1][0]
  B[2][1] = JH[0][0]
  B[2][2] = JH[1][1]
  B[2][3] = JH[0][1]
  B[2][4] = JH[1][2]
  B[2][5] = JH[0][2]
  B[2][6] = JH[1][3]
  B[2][7] = JH[0][3]
  return B

def gen_D():
  D = numpy.zeros((3,3),dtype=">f8")
  D[0][0] = 1
  D[0][1] = nu
  D[1][0] = nu
  D[1][1] = 1
  D[2][2] = (1-nu)/2
  D *= E/(1-nu**2)
  return D

def gauss_legendre(x,w,xyz):
  ke = numpy.zeros((dof*nen,dof*nen),dtype=">f8")
  D = gen_D()
  for j,eta in enumerate(x):
    for i,xi in enumerate(x):
      B = gen_B(xi,eta,xyz)
      BT = B.transpose()
      J = gen_J(xi,eta,xyz)
      detJ = numpy.linalg.det(J)
      ke += w[i] * w[j] * (BT@D@B) * detJ
  return ke

def gen_K(nn,ien,nint,cxyz):
  K = numpy.zeros((dof*nn,dof*nn),dtype=">f8")
  for i in range(len(ien)):
    ke = gen_ke(nint,ien[i],cxyz)
    K = merge_to_K(K,ke,ien[i])
  return K

def gen_ke(nint,ien,cxyz):
  xyz = cxyz[ien]
  x,w = numpy.polynomial.legendre.leggauss(nint)
  ke = gauss_legendre(x,w,xyz)
  return ke

def merge_to_K(K,ke,ien):
  for i in range(len(ien)):
    K[dof*ien[i]:dof*ien[i]+2,dof*ien[i]:dof*ien[i]+2] += ke[dof*i:dof*i+2,dof*i:dof*i+2]
    for j in range(i+1,len(ien)):
      K[dof*ien[i]:dof*ien[i]+2,dof*ien[j]:dof*ien[j]+2] += ke[dof*i:dof*i+2,dof*j:dof*j+2]
      K[dof*ien[j]:dof*ien[j]+2,dof*ien[i]:dof*ien[i]+2] += ke[dof*j:dof*j+2,dof*i:dof*i+2]
  return K

def get_fixed_ien(rng,ien):
  indices = numpy.argwhere(rng == support_boundary)
  fixed_ien = []
  for i in range(len(indices)):
    fixed_ien.append(ien[indices[i][0]][indices[i][1]])
    fixed_ien.append(ien[indices[i][0]][indices[i][1]-1])
  fixed_ien = numpy.unique(fixed_ien)
  return fixed_ien

def gen_fixed_u(fixed_ien):
  fixed_u = []
  for i in fixed_ien:
    fixed_u.extend([2*i, 2 * i + 1])
  fixed_u = sorted(fixed_u)
  return fixed_u

def get_load_ien(ien):
  load_ien = numpy.max(ien)
  return load_ien

def gen_U(nn,fixed_u):
  U = numpy.ones((dof*nn,2),dtype=">f8")
  for i in range(len(U)):
    U[i,0] = i
  U[fixed_u,1] = 0
  return U

def gen_F(nn,fixed_u,load_ien):
  F = numpy.zeros((dof*nn,2),dtype=">f8")
  for i in range(len(F)):
    F[i,0] = i
  F[fixed_u,1] = 1
  F[load_ien*2+1,1] = Py
  return F

def deform_matrix(K,U,F):
  for i in range(len(U)):
    if U[i,1] == 0:
      if numpy.all(U[i:-1,1]==0):
        return K,U,F
      k = 0
      for j in range(1,len(U)):
        if U[-j,1] != 0 and k == 0:
          K[[i, -j]] = K[[-j, i]]
          K[:, [i, -j]] = K[:, [-j, i]]
          U[[i, -j]] = U[[-j, i]]
          F[[i, -j]] = F[[-j, i]]
          k += 1

def split_matrix(K,U,F):
  for i in range(len(U)):
    if U[i,1] == 0:
      K1 = numpy.zeros((i,i),dtype=">f8")
      K2 = numpy.zeros((i,len(U)-i),dtype=">f8")
      K3 = numpy.zeros((len(U)-i,i),dtype=">f8")
      K4 = numpy.zeros((len(U)-i,len(U)-i),dtype=">f8")
      U_uk = numpy.zeros((i,2),dtype=">f8")
      U_k = numpy.zeros((len(U)-i,2),dtype=">f8")
      F_k = numpy.zeros((i,2),dtype=">f8")
      F_uk = numpy.zeros((len(U)-i,2),dtype=">f8")
      K1 = K[0:i,0:i]
      K2 = K[0:i,i:]
      K3 = K[i:,0:i]
      K4 = K[i:,i:]
      U_uk = U[0:i]
      U_k = U[i:]
      F_k = F[0:i]
      F_uk = F[i:]
      return K1, K2, K3, K4, U_uk, U_k, F_k, F_uk

def calc_displacement(K1,K2,U_uk,U_k,F_k):
  K1_inv = numpy.linalg.inv(K1)
  U_k = U_k[:,1]
  F_k = F_k[:,1]
  U_uk[:,1] = K1_inv @ (F_k - K2 @ U_k)
  return U_uk

def fix_U_uk(U_uk,fixed_u):
  U_uk = U_uk[U_uk[:,0].argsort()]
  for i in fixed_u:
    U_uk = numpy.insert(U_uk,i,[i, 0],axis=0)
  return U_uk

def print_matrix(matrix, block_size=2, name="Matrix"):
  print("="*5, name, "="*50)
  rows, cols = matrix.shape
  print("r",rows,"c",cols)
  for i in range(0, rows, block_size):
    for j in range(block_size):
      row = []
      for k in range(0, cols, block_size):
        row.append(" ".join(f"{matrix[i + j, k + l]:5.1f}" for l in range(block_size)))
      print("   ".join(row))
    print() 

def main():
  import argparse
  parser = argparse.ArgumentParser(description="""\
  solving simple beam problem with FEM
""")
  parser.add_argument("config", metavar="config", help="input config")
  parser.add_argument("-o", "--output", metavar="output-file", help="output file")
  parser.add_argument("--output_x", metavar="output-file", help="output file")
  parser.add_argument("--output_y", metavar="output-file", help="output file")
  options = parser.parse_args()

  import watfio
  factory = watfio.ParserFactory(options.config)
  parser = factory.build()
  cfg = parser.parse()
  import wataruel
  mf = wataruel.MeshFactory(cfg,options.config)
  mesh = mf.newInstance()
  nn = mesh.getNumberOfNodes()
  ne = mesh.getNumberOfElements()
  nsd = mesh.getNumberOfSpatialDimensions()
  npd = mesh.getNumberOfParametricDimensions()
  order = mesh.getOrder()[0][0]
  order = [ order for _ in range(npd)]
  cxyz = mesh.getPosition()
  ien = mesh.getIen()
  rng = mesh.getRng()

  fixed_ien = get_fixed_ien(rng,ien)
  fixed_u = gen_fixed_u(fixed_ien)
  load_ien = get_load_ien(ien)

  K = gen_K(nn,ien,nint,cxyz)
  U = gen_U(nn,fixed_u)
  F = gen_F(nn,fixed_u,load_ien)
  K,U,F = deform_matrix(K,U,F)
  K1, K2, K3, K4, U_uk, U_k, F_k, F_uk = split_matrix(K,U,F)
  U_uk = calc_displacement(K1,K2,U_uk,U_k,F_k)
  U_uk = fix_U_uk(U_uk,fixed_u)

  if(DEBUG):
    print("nn",nn)
    print("ne",ne)
    print("nsd",nsd)
    print("npd",npd)
    print("order",order)
    print("cxyz",cxyz)
    print("ien",ien)
    print("rng",rng)
    print("fixed_ien",fixed_ien)
    print("fixed_u",fixed_u)
    print("load_ien",load_ien)
    print("final K","="*150)
    print("k shape", K.shape)
    print_matrix(K,name="K")

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

