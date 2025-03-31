#!/bin/sh
# Created: Oct, 27, 2024 21:07:23 by Wataru Fukuda
set -eu

ELE_X=$1
ELE_Y=$2
RANGE_X=10
RANGE_Y=1

BASE=$(readlink -f $(dirname $0))
MESH=MESH
MESH_GEN_REPO=https://github.com/watf-dev/MeshGeneration.git
MESH_GEN_DIR=MeshGeneration/FEM
OUTPUT=output

### Ensure MeshGeneration repository exists
if [ ! -d $MESH_GEN_DIR ]; then
  echo "Cloning MeshGeneration repository..."
  git clone "$MESH_GEN_REPO"
else
  echo "MeshGeneration repository already exists."
fi

### Generate mesh
if [ ! -d $MESH ]; then
  ./$MESH_GEN_DIR/src/gen_mesh_FEM.py -o $MESH -e $ELE_X -e $ELE_Y -s 0 $RANGE_X -s 0 $RANGE_Y -p 1 -p 1 -n 2
  gen_xdmf.py $MESH/mesh.cfg -o mesh.xmf2
else
  echo "Mesh exists"
fi

### Run FEM solver
$BASE/FEM_solver.py $MESH/mesh.cfg --output_dir $OUTPUT --output_dis dis --output_disx disx --output_disy disy --output_nxx nxx --output_nyy nyy --output_nxy nxy --y_positive_flag

### Generate XDMF files
gen_xdmf.py $MESH/mesh.cfg -i $OUTPUT --fs dis n2f dis --fs disx n1f disx --fs disy n1f disy_abs -o dis.xmf2 
gen_xdmf.py $MESH/mesh.cfg -i $OUTPUT --fs nxx n1f nxx --fs nyy n1f nyy --fs nxy n1f nxy -o stress.xmf2 

