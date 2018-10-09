cmake_minimum_required(VERSION 2.8 FATAL_ERROR)

project(processing_sem3d)

find_package(PCL 1.8 REQUIRED)
find_package(Boost 1.40 COMPONENTS program_options REQUIRED)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

#Searching CUDA
FIND_PACKAGE(CUDA)

#Include the FindCUDA script
INCLUDE(FindCUDA)
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIR} )

cuda_add_executable (processing_sem3d src/processing_sem3d.cpp)
target_link_libraries (processing_sem3d ${PCL_LIBRARIES})

TARGET_LINK_LIBRARIES( processing_sem3d LINK_PUBLIC ${Boost_LIBRARIES} )