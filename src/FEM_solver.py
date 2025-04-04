#!/usr/bin/env python3
# Created: Nov, 05, 2024 15:10:16 by Wataru Fukuda

# DEBUG = True
DEBUG = False

import os
import numpy
import watfio
import watfel

### setting ###
DOF = 2  # degree of freedom
NEN = 4  # number of element nodes
NINT = 2  # number of integral points
SUPPORT_BOUNDARY = 1  ## todo: error with 2,3

## edit here ##
E = 4000000  # Young's modulus [kN/m^2]
NU = 0.3  # Poisson's ratio
PY = -1  ## any value except 1 [kN]

class watfFEM():
  def __init__(self, config, dof, nen, nint, support_boundary, E, nu, Py):
    factory = watfio.ParserFactory(config)
    parser = factory.build()
    cfg = parser.parse()
    mf = watfel.MeshFactory(cfg)
    mesh = mf.newInstance()
    self.nn = mesh.getNumberOfNodes()
    self.ne = mesh.getNumberOfElements()
    self.nsd = mesh.getNumberOfSpatialDimensions()
    self.npd = mesh.getNumberOfParametricDimensions()
    self.cxyz = mesh.getPosition()
    self.dof = dof
    self.nen = nen
    self.ien = cfg.getData("ien",int).reshape(self.ne,self.nen)
    self.rng = cfg.getData("rng",int).reshape(self.ne,self.nen)
    self.nint = nint
    self.support_boundary = support_boundary
    self.E = E
    self.nu = nu
    self.Py = Py
  def get_fixed_ien(self):
    indices = numpy.argwhere(self.rng == self.support_boundary)
    fixed_ien = []
    for i in range(len(indices)):
      fixed_ien.append(self.ien[indices[i][0]][indices[i][1]])
      fixed_ien.append(self.ien[indices[i][0]][indices[i][1]-1])
    fixed_ien = numpy.unique(fixed_ien)
    return fixed_ien
  def gen_fixed_u(self,fixed_ien):
    fixed_u = []
    for i in fixed_ien:
      fixed_u.extend([2*i, 2 * i + 1])
    fixed_u = sorted(fixed_u)
    return fixed_u
  def get_load_ien(self):
    load_ien = numpy.max(self.ien)
    return load_ien
  def gen_K(self):
    K = numpy.zeros((self.dof*self.nn,self.dof*self.nn),dtype=">f8")
    for i in range(len(self.ien)):
      ke = self._gen_ke(self.ien[i])
      K = self._merge_to_K(K,ke,self.ien[i])
    return K
  def gen_U(self,fixed_u):
    U = numpy.ones((self.dof*self.nn,2),dtype=">f8")
    for i in range(len(U)):
      U[i,0] = i
    U[fixed_u,1] = 0
    return U
  def gen_F(self,fixed_u,load_ien):
    F = numpy.zeros((self.dof*self.nn,2),dtype=">f8")
    for i in range(len(F)):
      F[i,0] = i
    F[fixed_u,1] = 1
    F[load_ien*2+1,1] = self.Py
    return F
  def deform_matrix(self,K,U,F):
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
  def split_matrix(self,K,U,F):
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
  def calc_displacement(self,K1,K2,U_uk,U_k,F_k):
    K1_inv = numpy.linalg.inv(K1)
    U_k = U_k[:,1]
    F_k = F_k[:,1]
    U_uk[:,1] = K1_inv @ (F_k - K2 @ U_k)
    return U_uk
  def fix_U_uk(self,U_uk,fixed_u):
    U_uk = U_uk[U_uk[:,0].argsort()]
    for i in fixed_u:
      U_uk = numpy.insert(U_uk,i,[i, 0],axis=0)
    return U_uk
  def get_stress(self,dis_file):
    dis_ = numpy.array(dis_file).reshape((-1,self.nsd))
    nxx_cp = []
    nyy_cp = []
    nxy_cp = []
    C = self._gen_D()
    x,w = numpy.polynomial.legendre.leggauss(self.nint)
    for i in range(self.ne):
      xyz = self.cxyz[self.ien[i]]
      dis = numpy.array(dis_[self.ien[i]]).reshape((-1,1))
      nxx_gp = []
      nyy_gp = []
      nxy_gp = []
      for eta in x:
        for xi in x:
          B = self._gen_B(xi,eta,xyz)
          stress_gp = C @ B @ dis
          nxx_gp.append(stress_gp[0])
          nyy_gp.append(stress_gp[1])
          nxy_gp.append(stress_gp[2])
      e_matrix = self._gen_e_matrix()
      nxx_cp.append(e_matrix @ nxx_gp)
      nyy_cp.append(e_matrix @ nyy_gp)
      nxy_cp.append(e_matrix @ nxy_gp)
    return numpy.array(nxx_cp), numpy.array(nyy_cp), numpy.array(nxy_cp)
  def ave_stress(self,stress):
    ien = self.ien
    stress = numpy.array(stress).reshape(-1,self.nen)
    result = numpy.zeros((self.nn),dtype=">f8")
    for n in range(self.nn):
      num = 0
      for i,ien_tmp in enumerate(ien):
        for j,ien_ in enumerate(ien_tmp):
          if n==ien_:
            result[n] += stress[i][j]
            num += 1
      result[n] /= num
    return result
  def print_debug(self,fixed_ien,fixed_u,load_ien,K):
    print("nn",self.nn)
    print("ne",self.ne)
    print("nsd",self.nsd)
    print("npd",self.npd)
    # print("order",self.order)
    print("cxyz",self.cxyz)
    print("ien",self.ien)
    print("rng",self.rng)
    print("fixed_ien",fixed_ien)
    print("fixed_u",fixed_u)
    print("load_ien",load_ien)
    print("final K","="*150)
    print("k shape",K.shape)
    self._print_matrix(K,name="K")

  def _gen_e_matrix(self):
    x,w = numpy.polynomial.legendre.leggauss(self.nint)
    M = numpy.zeros((4,4),dtype=">f8")
    counter = 0
    for eta in x:
      for xi in x:
        N = self._gen_N(xi, eta)
        M[counter] = N
        counter += 1
    M[[2,3]] = M[[3,2]]
    return numpy.linalg.inv(M)
  def _gen_N(self, xi, eta):
    N1 = 1/4 * (1.0-xi) * (1.0-eta)
    N2 = 1/4 * (1.0+xi) * (1.0-eta)
    N3 = 1/4 * (1.0+xi) * (1.0+eta)
    N4 = 1/4 * (1.0-xi) * (1.0+eta)
    # N3 = 1/4 * (1.0+xi) * (1.0+eta)
    # N4 = 1/4 * (1.0-xi) * (1.0+eta)
    N = numpy.array([N1,N2,N3,N4],dtype=">f8")
    return N
  def _gen_H(self,xi,eta):
    H = numpy.zeros((self.dof,self.nen),dtype=">f8")
    H[0][0] = 1/4 * (1 - eta) * (-1)
    H[0][1] = 1/4 * (1 - eta)
    H[0][2] = 1/4 * (1 + eta) 
    H[0][3] = 1/4 * (1 + eta) * (-1)
    H[1][0] = 1/4 * (1 - xi) * (-1)
    H[1][1] = 1/4 * (1 + xi) * (-1)
    H[1][2] = 1/4 * (1 + xi)
    H[1][3] = 1/4 * (1 - xi)
    return H
  def _gen_J(self,xi,eta,xyz):
    return self._gen_H(xi, eta)@xyz
  def _gen_B(self,xi,eta,xyz):
    J = self._gen_J(xi,eta,xyz)
    J_inv = numpy.linalg.inv(J)
    H = self._gen_H(xi,eta)
    JH = J_inv@H
    B = numpy.zeros((3,self.dof*self.nen),dtype=">f8")
    B = numpy.zeros((3, self.dof * self.nen))
    B[0, ::2] = JH[0]
    B[1, 1::2] = JH[1]
    B[2, ::2] = JH[1]
    B[2, 1::2] = JH[0]
    return B
  def _gen_D(self):
    D = numpy.zeros((3,3),dtype=">f8")
    D[0][0] = 1
    D[0][1] = self.nu
    D[1][0] = self.nu
    D[1][1] = 1
    D[2][2] = (1-self.nu)/2
    D *= self.E/(1-self.nu**2)
    return D
  def _gauss_legendre(self,x,w,xyz):
    ke = numpy.zeros((self.dof*self.nen,self.dof*self.nen),dtype=">f8")
    D = self._gen_D()
    for j,eta in enumerate(x):
      for i,xi in enumerate(x):
        B = self._gen_B(xi,eta,xyz)
        BT = B.transpose()
        J = self._gen_J(xi,eta,xyz)
        detJ = numpy.linalg.det(J)
        ke += w[i] * w[j] * (BT@D@B) * detJ
    return ke
  def _gen_ke(self,ien):
    xyz = self.cxyz[ien]
    x,w = numpy.polynomial.legendre.leggauss(self.nint)
    ke = self._gauss_legendre(x,w,xyz)
    return ke
  def _merge_to_K(self, K,ke,ien):
    for i in range(len(ien)):
      K[self.dof*ien[i]:self.dof*ien[i]+2,self.dof*ien[i]:self.dof*ien[i]+2] += ke[self.dof*i:self.dof*i+2,self.dof*i:self.dof*i+2]
      for j in range(i+1,len(ien)):
        K[self.dof*ien[i]:self.dof*ien[i]+2,self.dof*ien[j]:self.dof*ien[j]+2] += ke[self.dof*i:self.dof*i+2,self.dof*j:self.dof*j+2]
        K[self.dof*ien[j]:self.dof*ien[j]+2,self.dof*ien[i]:self.dof*ien[i]+2] += ke[self.dof*j:self.dof*j+2,self.dof*i:self.dof*i+2]
    return K
  def _print_matrix(self,matrix, block_size=2, name="Matrix"):
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
  parser.add_argument("config", help="Input configuration file")
  parser.add_argument("--output_dir", help="Output dir")
  parser.add_argument("--output_dis", help="Output file for displacement")
  parser.add_argument("--output_disx", help="Output file for X-displacement")
  parser.add_argument("--output_disy", help="Output file for Y-displacement")
  parser.add_argument("--output_nxx", help="Output file for normal stress in x")
  parser.add_argument("--output_nyy", help="Output file for normal stress in y")
  parser.add_argument("--output_nxy", help="Output file for shear stress")
  parser.add_argument("--y_positive_flag", action="store_true", help="Inverse y value from negative to positive")
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
    if options.y_positive_flag:
      U_uk_y *= -1
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

