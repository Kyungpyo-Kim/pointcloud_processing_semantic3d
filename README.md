# pointcloud_processing_semantic3d
Point cloud processing for preparing learning dataset of "Semantic3d"

## Dependencies
* Ubuntu16.04
* PCL1.8 (c++)
* python-pcl [link](https://github.com/strawlab/python-pcl) 
* vtk (python)
* vtkplotter [link](https://github.com/marcomusy/vtkplotter)
* h5py (python)

## Build

```bash
.../$ mkdir build && cd build
.../build$ cmake ..
.../build$ make
```

## Run
```bash
.../build$ ./processing_sem3d [log_file_name] [data_file_path] [label_file_path]
#./processing_sem3d log_181009.txt ../data/sem8_labels_training/bildstein_station1_xyz_intensity_rgb.txt ../data/sem8_labels_training/bildstein_station1_xyz_intensity_rgb.labels

```

## Automated bash
```bash
.../build$ ../auto_clustering.sh
```

## Visualization
```bash
.../build$ python ../scripts/pcd_visualization.py -r .
```
