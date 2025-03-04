all:
	echo "Hi there, do something else"

download-comp-data:
	python -c "from polaris_asap_poses.download import download_comp_data; download_comp_data();"
