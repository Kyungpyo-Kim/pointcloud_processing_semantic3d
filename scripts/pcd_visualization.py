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

parser = argparse.ArgumentParser(description = "Visualization tool of *.pcd file")
parser.add_argument("-r", "--root", help="root path including *.pcd files", required=True)

args = parser.parse_args()

root_path = os.path.abspath(args.root)


""" Find *.pcd files recursively """
pcd_file_list = []

for root, dirs, files in os.walk(root_path):
    rootpath = os.path.join(os.path.abspath(root_path), root)

    for file in files:
        if file.split('.')[-1] == 'pcd':
            filepath = os.path.join(rootpath, file)
            pcd_file_list.append(filepath)
            # print filepath


""" Convert *.pcd files to *.png using visualization tools """
vp = vtkplotter.Plotter()
for pcd_file in pcd_file_list:
    pcd = pcl.load(pcd_file)
    np_cloud = np.asarray(pcd)
    
    vp.points(np_cloud.tolist())
    vp.render()
    
    vp.screenshot(pcd_file.split('.')[0] + ".png")
    
    vp.clear()
    
