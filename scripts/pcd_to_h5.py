# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 09:27:50 2018

@author: kyungpyo94@gmail.com
"""

## argument
import argparse

## system
import os, sys

## pcl and visualization
import pcl
import vtkplotter

## numpy
import numpy as np

#h5py
import h5py

""" Set arguments and parse them"""

parser = argparse.ArgumentParser(description = "Visualization tool of *.pcd file")
parser.add_argument("-r", "--root", help="root path including *.pcd files", required=True)
parser.add_argument("-o", "--out_path", help="directory of output", required=True)
parser.add_argument("-v", "--vox_grid", type=float, help="voxel filter size", required=True)
parser.add_argument("-p", "--point_num", type=int, help="point number", required=True)

args = parser.parse_args()


""" Set path and make output folder """

root_path = os.path.abspath(args.root)

out_path = os.path.abspath(args.out_path)
if not os.path.exists(out_path):
    os.mkdir(out_path)


""" Find *.pcd files recursively """

pcd_file_list = []

for root, dirs, files in os.walk(root_path):
    rootpath = os.path.join(os.path.abspath(root_path), root)

    for file in files:
        if file.split('.')[-1] == 'pcd':
            filepath = os.path.join(rootpath, file)
            pcd_file_list.append(filepath)
#            print filepath
            

""" Make log file """

def log_string(f_log, out_str):
    f_log.write(out_str+'\n')
    f_log.flush()
    print(out_str)
    
f_log = open(os.path.join(out_path, "log.txt"), 'w')

log_string(f_log, "\n\n[Start pcd conversion to h5]")
log_string(f_log,  str(args) )


""" Load point cloud data """
log_string(f_log, "\n\n:: Load point cloud data")

cls_to_label = {0: 'unknown',
                1: 'car',
                2: 'truck',
                3: 'bike',
                4: 'pedestrian',
                5: 'tree',
                6: 'wall',
                7: 'bus'}

label_to_cls = {'unknown' : 0,
                'car': 1,
                'truck': 2,
                'bike': 3,
                'pedestrian' : 4,
                'tree' : 5,
                'wall' : 6,
                'bus': 7}
                
sem3d_label_to_cls = { 'buildings' : 6,
                      'cars' : 1,
                      'hard scape' : 0,
                      'high vegetation' : 5,
                      'low vegetation' : 5,
                      'man made terrian' : 0,
                      'nature terrain' : 0,
                      'scanning artefacts' : 0}
    
all_pcl_point_cloud = [ [] for _ in range(len(label_to_cls)) ]

for pcd_file in pcd_file_list:

    cloud = pcl.load(pcd_file)
    sem3d_label = pcd_file.split("/")[-1].split("_")[0]
    cls = sem3d_label_to_cls[sem3d_label]
    
    all_pcl_point_cloud[cls].append(cloud)
    
for i in range(len(all_pcl_point_cloud)):
    log_string(f_log, "::   * Class {} : {}" .format(cls_to_label[i], len(all_pcl_point_cloud[i])))


""" Sample point cloud data """
log_string(f_log, "\n\n:: Sample point cloud data")

vox_grid_size = args.vox_grid
vox_pcl_point_cloud = [ [] for _ in range(len(label_to_cls)) ]

for cls in range(len(all_pcl_point_cloud)):
    
    for pcl_pc in all_pcl_point_cloud[cls]:

        vgf = pcl_pc.make_voxel_grid_filter()
        vgf.set_leaf_size(vox_grid_size, vox_grid_size, vox_grid_size)
        
        cloud_filtered = vgf.filter()
        
        vox_pcl_point_cloud[cls].append(cloud_filtered)


for i in range(len(vox_pcl_point_cloud)):
    log_string(f_log, "::   * Class {} : {}" .format(cls_to_label[i], len(vox_pcl_point_cloud[i])))
                
#        vp = vtkplotter.Plotter()
#        vp.points(np_cloud.tolist())
#        vp.show()
#        #vp.screenshot(pcd_file.split('.')[0] + ".png")
#        vp.interactor.TerminateApp()
#        vp.interactor.GetRenderWindow().Finalize()
#        vp.interactor.TerminateApp()
#        del vp.renderWin, vp.interactor, vp
    
    
""" Data augmentation """
log_string(f_log, "\n\n:: Data augmentation")
log_string(f_log, ":: !!pitch * yaw * point_cloud!!")

yaw_rotate_from = 0.
yaw_rotate_to = 360.
yaw_step = 20.

pitch_rotate_from = -15.
pitch_rotate_to = 15.
pitch_step = 10.

log_string(f_log, "::   * Configuration")
log_string(f_log, "::     + yaw_rotate_from: {}".format(yaw_rotate_from))
log_string(f_log, "::     + yaw_rotate_to: {}".format(yaw_rotate_to))
log_string(f_log, "::     + yaw_step: {}".format(yaw_step))
log_string(f_log, "::     + pitch_rotate_from: {}".format(pitch_rotate_from))
log_string(f_log, "::     + pitch_rotate_to: {}".format(pitch_rotate_to))
log_string(f_log, "::     + pitch_step: {}".format(pitch_step))

aug_np_point_cloud = [ [] for _ in range(len(label_to_cls)) ]

for cls in range(len(vox_pcl_point_cloud)):
    
    if cls == label_to_cls['cars']:
        out_cls_visu_path = os.path.join(out_path, cls_to_label[cls])
        if not os.path.exists(out_cls_visu_path):
            os.mkdir(out_cls_visu_path)
        out_cls_visu_path = os.path.join(out_cls_visu_path, "visu")
        if not os.path.exists(out_cls_visu_path):
            os.mkdir(out_cls_visu_path)
        
        cnt = 0
                    
        for pcl_pc in vox_pcl_point_cloud[cls]:
            
            for yaw in np.arange(yaw_rotate_from, yaw_rotate_to, \
            (yaw_rotate_to - yaw_rotate_from) / yaw_step):
                
                yaw = yaw * np.pi / 180.0
                
                for pitch in np.arange(pitch_rotate_from, pitch_rotate_to, \
                (pitch_rotate_to - pitch_rotate_from) / pitch_step):                       
                    
                    pitch = pitch * np.pi / 180.0
                    
                    yawMatrix = np.matrix([[np.cos(yaw), -np.sin(yaw), 0.],
                                           [np.sin(yaw), np.cos(yaw), 0.],
                                           [0., 0., 1.]])
                    
                    pitchMatrix = np.matrix([[np.cos(pitch), 0., np.sin(pitch)],
                                             [0., 1., 0.],
                                             [-np.sin(pitch), 0., np.cos(pitch)]])
                                             
                    np_pc = np.asarray(pcl_pc)
                                       
                    np_pc[:,0] -= np.mean(np_pc[:,0])
                    np_pc[:,1] -= np.mean(np_pc[:,1])
                    np_pc[:,2] -= np.mean(np_pc[:,2])
                                    
                    np_pc_aug = np.array((pitchMatrix*yawMatrix*np_pc.T).T)                
                        
                    vp = vtkplotter.Plotter()
                    vp.points(np_pc_aug.tolist())
                    vp.render()
                    vp.screenshot(out_cls_visu_path + "/visu_{:04}.png".format(cnt))
                    cnt+=1
                    vp.interactor.TerminateApp()
                    vp.interactor.GetRenderWindow().Finalize()
                    vp.interactor.TerminateApp()
                    del vp.renderWin, vp.interactor, vp
                                    
                    aug_np_point_cloud[cls].append(np_pc_aug)
    else:
        out_cls_visu_path = os.path.join(out_path, cls_to_label[cls])
        if not os.path.exists(out_cls_visu_path):
            os.mkdir(out_cls_visu_path)
        out_cls_visu_path = os.path.join(out_cls_visu_path, "visu")
        if not os.path.exists(out_cls_visu_path):
            os.mkdir(out_cls_visu_path)
        
        cnt = 0
                    
        for pcl_pc in vox_pcl_point_cloud[cls]:
                                                         
            np_pc = np.asarray(pcl_pc)
                               
            np_pc[:,0] -= np.mean(np_pc[:,0])
            np_pc[:,1] -= np.mean(np_pc[:,1])
            np_pc[:,2] -= np.mean(np_pc[:,2])
                            
            np_pc_aug = np.copy(np_pc)         
                
            vp = vtkplotter.Plotter()
            vp.points(np_pc_aug.tolist())
            vp.render()
            vp.screenshot(out_cls_visu_path + "/visu_{:04}.png".format(cnt))
            cnt+=1
            vp.interactor.TerminateApp()
            vp.interactor.GetRenderWindow().Finalize()
            vp.interactor.TerminateApp()
            del vp.renderWin, vp.interactor, vp
                            
            aug_np_point_cloud[cls].append(np_pc_aug)
                                         
                                         
for i in range(len(aug_np_point_cloud)):
    log_string(f_log, "::   * Class {} : {}" .format(cls_to_label[i], len(aug_np_point_cloud[i])))


""" Generate h5 files """
log_string(f_log, "\n\n:: Generate h5 files")

## Configuration 
POINT_NUM = args.point_num
INPUT_DIM = 3 ## x, y, z
H5_BATCH_SIZE = 100 

data_dtype = 'float32'
label_dtype = 'uint8'

data_dim = [POINT_NUM, INPUT_DIM]
label_dim = [1]


log_string(f_log, "::   * Configuration")
log_string(f_log, "::     + POINT_NUM: {}".format(POINT_NUM))
log_string(f_log, "::     + INPUT_DIM: {}".format(INPUT_DIM))
log_string(f_log, "::     + H5_BATCH_SIZE: {}".format(H5_BATCH_SIZE))
log_string(f_log, "::     + data_dtype: {}".format(data_dtype))
log_string(f_log, "::     + label_dtype: {}".format(label_dtype))


log_string(f_log, "::   * Normalization")
norm_resampling_np_point_cloud = [ [] for _ in range(len(label_to_cls)) ]

# Data normalization and resampling
def NormalizeResample(data, num_sample):
    """ data is in N x ...
    we want to keep num_samplexC of them.
    if N > num_sample, we will randomly keep num_sample of them.
    if N < num_sample, we will randomly duplicate samples.
    """
    ## normalizing   
    x_min = float(data[:,0].min())
    x_max = float(data[:,0].max())
    y_min = float(data[:,1].min())
    y_max = float(data[:,1].max())
    z_min = float(data[:,2].min())
    z_max = float(data[:,2].max())
      
    data[:,0] = data[:,0] - x_min
    data[:,1] = data[:,1] - y_min
    data[:,2] = data[:,2] - z_min
      
    data[:,0] = data[:,0] / float(x_max - x_min)
    data[:,1] = data[:,1] / float(y_max - y_min)
    data[:,2] = data[:,2] / float(z_max - z_min)
                 
    ## resampling
    N = data.shape[0]
    if (N == num_sample):
        return data
    elif (N > num_sample):
        sample = np.random.choice(N, num_sample)
        return data[sample, ...]
    else:
        sample = np.random.choice(N, num_sample-N)
        dup_data = data[sample, ...]
        return np.concatenate([data, dup_data], 0)

for cls in range(len(aug_np_point_cloud)):
    for np_pc in aug_np_point_cloud[cls]:
        norm_np_pc = NormalizeResample(np_pc, POINT_NUM)      
        norm_resampling_np_point_cloud[cls].append(norm_np_pc)
    
log_string(f_log, "::   * Generate and save h5 files")

def save_h5_files(data, cls, H5_BATCH_SIZE, out_cls_path, data_dtype, label_dtype):
    
    if len(data) > 0 : print data[0]
    file_cnt = 0
    while len(data) > 0:
        if len(data) >= H5_BATCH_SIZE:
            
            data_h5 = np.array(data[0])            
            print data[0].shape
            print data_h5
            
            cls_h5 = [cls for _ in range(H5_BATCH_SIZE)]
            del data[:H5_BATCH_SIZE]
            file_name_path = os.path.join(out_cls_path, "sem3d_h5_{:04}.h5".format(file_cnt))
                        
            h5_fout = h5py.File(file_name_path)
            h5_fout.create_dataset('data', data=data_h5, compression='gzip', 
                                   compression_opts=4, dtype=data_dtype)
            h5_fout.create_dataset('label', data=cls_h5, compression='gzip', 
                                   compression_opts=1, dtype=label_dtype)
            h5_fout.close()
            log_string(f_log, "::     - Generate {}".format(file_name_path))
            
        elif not len(data) == 0:
            data_h5 = data
            cls_h5 = [cls for _ in range(len(data))]
            del data
            
            file_name_path = os.path.join(out_cls_path, "sem3d_h5_{:04}.h5".format(file_cnt))
            
            h5_fout = h5py.File(file_name_path)
            h5_fout.create_dataset('data', data=data_h5, compression='gzip', 
                                   compression_opts=4, dtype=data_dtype)
            h5_fout.create_dataset('label', data=cls_h5, compression='gzip', 
                                   compression_opts=1, dtype=label_dtype)
            h5_fout.close()
            log_string(f_log, "::     - Generate {}".format(file_name_path))
            
            
        file_cnt +=1
    
for cls in range(len(norm_resampling_np_point_cloud)):
    label = cls
    
    ## make directory to save
    out_cls_path = os.path.join(out_path, cls_to_label[cls])
    if not os.path.exists(out_cls_path):
        os.mkdir(out_cls_path)
        
    ## save h5 file    
    save_h5_files(norm_resampling_np_point_cloud[cls], cls, H5_BATCH_SIZE, \
                    out_cls_path, data_dtype, label_dtype)
                    
    
    
    
        
        