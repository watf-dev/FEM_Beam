#!/usr/bin/env python3
# Created: Jan, 28, 2025 11:49:45 by Wataru Fukuda

import os
import numpy
import watfio
import wataruel

class watfFEM():
  def __init__(self, config, dof, nen, nint, support_boundary, E, nu, Py):
    factory = watfio.ParserFactory(config)
    parser = factory.build()
    cfg = parser.parse()
    mf = wataruel.MeshFactory(cfg,config)
    mesh = mf.newInstance()
    self.nn = mesh.getNumberOfNodes()
    self.ne = mesh.getNumberOfElements()
    self.nsd = mesh.getNumberOfSpatialDimensions()
    self.npd = mesh.getNumberOfParametricDimensions()
    order = mesh.getOrder()[0][0]
    self.order = [ order for _ in range(self.npd)]
    self.cxyz = mesh.getPosition()
    self.ien = mesh.getIen()
    self.rng = mesh.getRng()
    self.dof = dof
    self.nen = nen
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
  def print_debug(self,fixed_ien,fixed_u,load_ien,K):
    print("nn",self.nn)
    print("ne",self.ne)
    print("nsd",self.nsd)
    print("npd",self.npd)
    print("order",self.order)
    print("cxyz",self.cxyz)
    print("ien",self.ien)
    print("rng",self.rng)
    print("fixed_ien",fixed_ien)
    print("fixed_u",fixed_u)
    print("load_ien",load_ien)
    print("final K","="*150)
    print("k shape",K.shape)
    self._print_matrix(K,name="K")

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

