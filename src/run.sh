#!/bin/sh
# Created: Oct, 27, 2024 21:07:23 by Wataru Fukuda
set -eu

ELE_X=$1
ELE_Y=$2

BASE=${pwd}
MESH=MESH
MESH_GEN_REPO=https://github.com/watf-dev/MeshGeneration.git
MESH_GEN_DIR=MeshGeneration/FEM

### Ensure MeshGeneration repository exists
if [ ! -d $MESH_GEN_DIR ]; then
    echo "Cloning MeshGeneration repository..."
    git clone "$MESH_GEN_REPO"
else
    echo "MeshGeneration repository already exists."
fi

### Generate mesh
./$MESH_GEN_DIR/src/gen_mesh_FEM.py -o $MESH -e $ELE_X -e $ELE_Y -s 0 $ELE_X -s 0 $ELE_Y -p 1 -p 1 -n 2
gen_xdmf_wataf.py $MESH/mesh.cfg -o mesh.xmf2

### Run FEM solver
$BASE/src/FEM_solver.py $MESH/mesh.cfg -o dis --output_x dis_x --output_y dis_y --output_nxx nxx --output_nyy nyy --output_nxy nxy

### Generate XDMF files
gen_xdmf_wataf.py $MESH/mesh.cfg --fs dis n2f dis -o dis.xmf2
gen_xdmf_wataf.py $MESH/mesh.cfg --fs dis_x n1f dis_x -o dis_x.xmf2
gen_xdmf_wataf.py $MESH/mesh.cfg --fs dis_y n1f dis_y -o dis_y.xmf2
gen_xdmf_wataf.py $MESH/mesh.cfg --fs nxx n1f nxx -o nxx.xmf2
gen_xdmf_wataf.py $MESH/mesh.cfg --fs nyy n1f nyy -o nyy.xmf2
gen_xdmf_wataf.py $MESH/mesh.cfg --fs nxy n1f nxy -o nxy.xmf2

