# pointcloud_processing_semantic3d
Point cloud processing for preparing learning dataset of "Semantic3d"

## Dependencies
* Ubuntu16.04
* PCL1.8

## Build

```bash
mkdir build && cd build
cmake ..
make
```

## Run
```bash
./processing_sem3d [log_file_name] [data_file_path] [label_file_path]
#./processing_sem3d log_181009.txt /data/semantic3d.txt /data/semantic3d.labels

```
