DATA_DIR_GNINA_TEST_CASE=./data/gnina-test-case/
DATA_DIR_LIGAND_SDF=./data/ligand_sdf/
DATA_DIR_MERS_REF_STRUCT=./data/raw/reference_structures/MERS-CoV-Mpro/
DATA_DIR_GNINA_OUT=./data/gnina-out/

all:
	echo "Hi there, do something else"

download-comp-data:
	python -c "from polaris_asap_poses.download import download_comp_data; download_comp_data();"

download-gnina:
	mkdir -p bin
	wget -O ./bin/gnina https://github.com/gnina/gnina/releases/download/v1.3/gnina
	chmod a+x ./bin/gnina
	echo "Done.  In order to run gnina, you may need to: sudo apt install nvidia-cuda-toolkit"

# https://colab.research.google.com/drive/1QYo5QLUE80N_G28PlpYs6OKGddhhd931?usp=sharing#scrollTo=WctyMpdMluFN
download-gnina-test-case:
	mkdir -p $(DATA_DIR_GNINA_TEST_CASE)
	# download pdb containing receptor and ligand
	wget http://files.rcsb.org/download/3ERK.pdb -O $(DATA_DIR_GNINA_TEST_CASE)/3ERK.pdb
	grep ATOM $(DATA_DIR_GNINA_TEST_CASE)/3ERK.pdb > $(DATA_DIR_GNINA_TEST_CASE)/rec.pdb
	grep SB4 $(DATA_DIR_GNINA_TEST_CASE)/3ERK.pdb > $(DATA_DIR_GNINA_TEST_CASE)/lig.pdb

dataprep:
	python polaris_asap_poses/dataprep.py

test-gnina-version:
	./bin/gnina --version

# The prebuilt gnina install fails:
#	terminate called after throwing an instance of 'c10::Error'
#  		what():  CUDA error: no kernel image is available for execution on the device
# 	Compile with `TORCH_USE_CUDA_DSA` to enable device-side assertions.
# Not interested in building gnina from scratch, which also requires building openbabel
# So use docker instead
test-gnina-prebuilt:
	./bin/gnina -r $(DATA_DIR_GNINA_TEST_CASE)/rec.pdb -l $(DATA_DIR_GNINA_TEST_CASE)/lig.pdb --autobox_ligand $(DATA_DIR_GNINA_TEST_CASE)/lig.pdb -o $(DATA_DIR_GNINA_TEST_CASE)/docked.sdf --seed 0

test-gnina-docker:
	time docker run -v $(shell pwd):/scr gnina/gnina gnina -r /scr/$(DATA_DIR_GNINA_TEST_CASE)/rec.pdb -l /scr/$(DATA_DIR_GNINA_TEST_CASE)/lig.pdb --autobox_ligand /scr/$(DATA_DIR_GNINA_TEST_CASE)/lig.pdb -o /scr/$(DATA_DIR_GNINA_TEST_CASE)/docked.sdf --seed 0

# This also fails:
#	/root/gnina/build/libmolgrid-prefix/src/libmolgrid/src/grid_maker.cu:288: no kernel image is available for execution on the deviceterminate called after throwing an instance of 'std::runtime_error'
#	  what():  CUDA Error: no kernel image is available for execution on the device
#	Command exited with non-zero status 139
test-gnina-docker-gpu:
	time docker run --gpus=all -v $(shell pwd):/scr gnina/gnina gnina -r /scr/$(DATA_DIR_GNINA_TEST_CASE)/rec.pdb -l /scr/$(DATA_DIR_GNINA_TEST_CASE)/lig.pdb --autobox_ligand /scr/$(DATA_DIR_GNINA_TEST_CASE)/lig.pdb -o /scr/$(DATA_DIR_GNINA_TEST_CASE)/docked.sdf --seed 0

# yes I do have a gpu and docker can at least kind of see it
test-docker-gpu:
	docker run --rm --gpus all nvidia/cuda:11.7.1-devel-ubuntu22.04 nvidia-smi


gnina-predict:
	mkdir -p $(DATA_DIR_GNINA_OUT)
	time docker run -v $(shell pwd):/scr gnina/gnina gnina -r /scr/$(DATA_DIR_MERS_REF_STRUCT)/protein.pdb -l /scr/$(DATA_DIR_LIGAND_SDF)/test_73_MERS-CoV-Mpro.sdf --autobox_ligand /scr/$(DATA_DIR_LIGAND_SDF)/test_73_MERS-CoV-Mpro.sdf -o /scr/$(DATA_DIR_GNINA_OUT)/docked_test_73_mers.sdf --seed 0

push-gnina-out:
	gsutil rsync -r data/gnina-out gs://alpha29-bfx/polaris-asap-poses/data/gnina-out

pull-gnina-out:
	gsutil rsync -r gs://alpha29-bfx/polaris-asap-poses/data/gnina-out data/gnina-out
