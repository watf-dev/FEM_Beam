# FEM solver for cantilever beam

## Configuration

![config pic](figs/config.png)

To edit the material properties in the setting section of `FEM_solver.py`, open the file and change values if needed;
- E: Young's modulus
- nu: Poisson's ratio
- Py: vertical load on the edge of right top

## Run
```
./src/run.sh 40 10
```
- arg1: the number of elements in x
- arg2: the number of elements in y
```
./src/run_steps.sh
```

## Example Results
### Comparison of Tip Displacement Across Different Configurations
![convergence](figs/convergence.png)

---

### The number of elments over height = 1
<p align="center">
  <img src="figs/disa_height1.png" width="400">
  <img src="figs/nxx_height1.png" width="400">
</p>
<p align="center">
  <img src="figs/nyy_height1.png" width="400">
  <img src="figs/nxy_height1.png" width="400">
</p>

---

### The number of elments over height = 4
<p align="center">
  <img src="figs/disa_height4.png" width="400">
  <img src="figs/nxx_height4.png" width="400">
</p>
<p align="center">
  <img src="figs/nyy_height4.png" width="400">
  <img src="figs/nxy_height4.png" width="400">
</p>

---

### The number of elments over height = 10
<p align="center">
  <img src="figs/disa_height10.png" width="400">
  <img src="figs/nxx_height10.png" width="400">
</p>
<p align="center">
  <img src="figs/nyy_height10.png" width="400">
  <img src="figs/nxy_height10.png" width="400">
</p>

---

### The element aspect ratio = 1
<p align="center">
  <img src="figs/disa_square.png" width="400">
  <img src="figs/nxx_square.png" width="400">
</p>
<p align="center">
  <img src="figs/nyy_square.png" width="400">
  <img src="figs/nxy_square.png" width="400">
</p>

## Appendix
### Cloning the Repository
To clone the repository with its submodules,
```
git clone --recurse-submodules https://github.com/watf-dev/FEM_Beam.git
```
To add the directory to the PATH, for example,
```
echo 'export PATH=$PATH:/path/to/directory' >> ~/.zshrc
source ~/.zshrc
```

### Mesh Generation
Currently, a TEST mesh is available in the public directory.


