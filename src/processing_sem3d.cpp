

/// c/c++, std
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <stdio.h>

#include <string>
#include <fstream>
#include <sstream>

#include <time.h>

#include <vector>

/// boost
#include <boost/format.hpp> 
#include <boost/lexical_cast.hpp>


/// pcl
#include <pcl/ModelCoefficients.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/features/normal_3d.h>
#include <pcl/kdtree/kdtree.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/segmentation/extract_clusters.h>

// The GPU specific stuff here
#include <pcl/gpu/octree/octree.hpp>
#include <pcl/gpu/containers/device_array.hpp>
#include <pcl/gpu/segmentation/gpu_extract_clusters.h>
#include <pcl/gpu/segmentation/impl/gpu_extract_clusters.hpp>


#define SEM3D_CLASS_NUM 9


/*
* --------------------------------------------------------------------------------------
* Sample 2. Java의 File.mkdirs( )와 비슷한 2 depth 이상의 디렉토리를 한번에 만드는 함수
*/

int mkdirs(const char *path, mode_t mode)
{
    char tmp_path[2048];
    const char *tmp = path;
    int  len  = 0;
    int  ret;

    if(path == NULL || strlen(path) >= 2048) {
        return -1;
    }

    while((tmp = strchr(tmp, '/')) != NULL) {
        len = tmp - path;
        tmp++;
        if(len == 0) {
            continue;
        }
        strncpy(tmp_path, path, len);
        tmp_path[len] = 0x00;

        if((ret = mkdir(tmp_path, mode)) == -1) {
            if(errno != EEXIST) {
                return -1;
            }
        }
    }

    return mkdir(path, mode);
}



/*
std::string split implementation by using delimeter as an another string
*/
std::vector<std::string> split(std::string stringToBeSplitted, std::string delimeter)
{
	std::vector<std::string> splittedString;
	int startIndex = 0;
	int  endIndex = 0;
	while( (endIndex = stringToBeSplitted.find(delimeter, startIndex)) < stringToBeSplitted.size() )
	{
 
		std::string val = stringToBeSplitted.substr(startIndex, endIndex - startIndex);
		splittedString.push_back(val);
		startIndex = endIndex + delimeter.size();
 
	}
	if(startIndex < stringToBeSplitted.size())
	{
		std::string val = stringToBeSplitted.substr(startIndex);
		splittedString.push_back(val);
	}
	return splittedString;
 
}

/**
 * @brief main of the program
 * @arg log file path
 * @arg data file path
 * @arg label file path
 */
int main (int argc, char** argv)
{
    if (argc != 4)
    {
        std::cout << "\n\n\n[Arguments error]" << std::endl;
        std::cout << "Check arguments!" << std::endl;
        std::cout << "  ex) ./processing_sem3d [log_file_path] [data_file_path] [label_file_path]\n\n\n";

        exit(1);
    }

    /// make output folder
    std::vector<std::string> data_path_split = split(argv[2], "/");
    std::vector<std::string> folder_split = split(data_path_split.back(), ".");
    std::string out_folder_path(folder_split[0]);
    out_folder_path = "./" + out_folder_path;

    mkdirs(out_folder_path.c_str(), 0777);
    
    /// make log file
    std::string out_log_path = out_folder_path + "/" + std::string(argv[1]);
    std::ofstream f_log(out_log_path.c_str());
    f_log << boost::format("[Start point cloud processing]") << std::endl;
    std::cout << boost::format("[Start point cloud processing]") << std::endl;

    /// Read point cloud data in the *.txt file

    std::ifstream f_data(argv[2]);
    f_log << boost::format("  - Open %1% file") % argv[2] << std::endl;
    std::cout << boost::format("  - Open %1% file") % argv[2] << std::endl;


    if (!f_data.is_open())
    {
        f_log << boost::format("Fail to open the %1% file") % argv[2] << std::endl;
        std::cerr << boost::format("Fail to open the %1% file") % argv[2] << std::endl;
        exit(1);
    }

    std::ifstream f_label(argv[3]);
    f_log << boost::format("  - Open %1% file") % argv[3] << std::endl;
    std::cout << boost::format("  - Open %1% file") % argv[3] << std::endl;

    if (!f_label.is_open())
    {
        f_log << boost::format("Fail to open the %1% file") % argv[3] << std::endl;
        std::cerr << boost::format("Fail to open the %1% file") % argv[3] << std::endl;
        exit(1);
    }

    ///   - parsing point cloud data
    std::vector<pcl::PointCloud<pcl::PointXYZ>::Ptr> point_cloud_ptr_array;
     /**
      * Label lists
      * 0: unlabeled points,
      * 1: man-made terrain, 
      * 2: natural terrain, 
      * 3: high vegetation, 
      * 4: low vegetation, 
      * 5: buildings, 
      * 6: hard scape, 
      * 7: scanning artefacts, 
      * 8: cars
      */
    std::vector<std::string> label_to_string_sem3d;
    label_to_string_sem3d.push_back("unlabeled points");
    label_to_string_sem3d.push_back("man-made terrain");
    label_to_string_sem3d.push_back("natural terrain");
    label_to_string_sem3d.push_back("high vegetation");
    label_to_string_sem3d.push_back("low vegetation");
    label_to_string_sem3d.push_back("buildings");
    label_to_string_sem3d.push_back("hard scape");
    label_to_string_sem3d.push_back("scanning artefacts");
    label_to_string_sem3d.push_back("cars");

    
    for (int i = 0; i < SEM3D_CLASS_NUM; i++)
    {
        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_temp(new pcl::PointCloud<pcl::PointXYZ>); 
        point_cloud_ptr_array.push_back(cloud_temp);
    }

    pcl::PCDWriter writer;

    clock_t tStart = clock();
        
    int cnt = 0;    
    
    f_log << "  - parsing point cloud data" << std::endl;
    std::cout << "  - parsing point cloud data" << std::endl;

    f_log << std::endl;
    std::cout << std::endl;

    while(!f_label.eof())   
    //for (int test_i = 0; test_i < 1000; test_i++)
    {
        std::cout << boost::format("\rProcessed points: %1%") % ++cnt;

        std::string line_data;
        std::string line_label;
        std::getline(f_data, line_data);
        std::getline(f_label, line_label);

        if(f_data.eof()) 
        {
            f_log << "\n\n  f_data.eof  \n\n" << std::endl;
            std::cerr << "\n\n  f_data.eof  \n\n" << std::endl;
            break;
        }
        if (line_label == std::string("")) 
        {
            f_log << "line_label == std::string("")" << std::endl;
            std::cerr << "line_label == std::string("")" << std::endl;
            break;
        }

        std::istringstream iss(line_data);
        std::vector<std::string> words_in_line((std::istream_iterator<std::string>(iss)), std::istream_iterator<std::string>());

        pcl::PointXYZ p;
        p.x = boost::lexical_cast<float>(words_in_line.at(0));
        p.y = boost::lexical_cast<float>(words_in_line.at(1));
        p.z = boost::lexical_cast<float>(words_in_line.at(2));

        int label = boost::lexical_cast<int>(line_label.at(0));

        point_cloud_ptr_array.at((size_t)label)->push_back(p);

    }

    f_log << std::endl;
    std::cout << std::endl;


    for (size_t i = 0 ; i < SEM3D_CLASS_NUM; i++)
    {
        f_log << boost::format("  - Total points[%1%]: %2%") % label_to_string_sem3d.at(i) % point_cloud_ptr_array.at(i)->size() << std::endl;
        std::cout << boost::format("  - Total points[%1%]: %2%") % label_to_string_sem3d.at(i) % point_cloud_ptr_array.at(i)->size() << std::endl;        
    } 
    f_log << boost::format("  - Execution time for parsing: %1%") % ((double)(clock() - tStart)/CLOCKS_PER_SEC) << std::endl;
    std::cout << boost::format("  - Execution time for parsing: %1%") % ((double)(clock() - tStart)/CLOCKS_PER_SEC) << std::endl;
   
    f_log << "[Start clustering]" << std::endl;
    std::cout << "[Start clustering]" << std::endl;

    float cluster_tolerance = 0.2; ///< 2cm
    int min_cluster_size = 100;
    int max_cluster_size = 100000;

    f_log << "  - Clustering parameters" << std::endl;
    f_log << "    * ClusterTolerance: " << cluster_tolerance << std::endl;
    f_log << "    * MinClusterSize: " << min_cluster_size << std::endl;
    f_log << "    * MaxClusterSize: " << max_cluster_size << std::endl;
    std::cout << "  - Clustering parameters" << std::endl;
    std::cout << "    * ClusterTolerance: " << cluster_tolerance << std::endl;
    std::cout << "    * MinClusterSize: " << min_cluster_size << std::endl;
    std::cout << "    * MaxClusterSize: " << max_cluster_size << std::endl;
    


    for(size_t i_pc_array = 0; i_pc_array <  point_cloud_ptr_array.size(); i_pc_array++)
    {
        tStart = clock();

        std::string cluster_folder_path = out_folder_path + "/" + label_to_string_sem3d.at(i_pc_array);
        mkdirs(cluster_folder_path.c_str(), 0777);

        if (point_cloud_ptr_array.at(i_pc_array)->size() == 0) continue;

        pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_filtered = point_cloud_ptr_array.at(i_pc_array);

        f_log << "  - Starting with the CPU version [" << label_to_string_sem3d.at(i_pc_array) << "]" << std::endl;
        std::cout << "  - Starting with the CPU version [" << label_to_string_sem3d.at(i_pc_array) << "]" << std::endl;

        // Creating the KdTree object for the search method of the extraction
        pcl::search::KdTree<pcl::PointXYZ>::Ptr tree (new pcl::search::KdTree<pcl::PointXYZ>);
        tree->setInputCloud (cloud_filtered);

        std::vector<pcl::PointIndices> cluster_indices;
        pcl::EuclideanClusterExtraction<pcl::PointXYZ> ec;
        ec.setClusterTolerance (cluster_tolerance); 
        ec.setMinClusterSize (min_cluster_size);
        ec.setMaxClusterSize (max_cluster_size);
        ec.setSearchMethod (tree);
        ec.setInputCloud( cloud_filtered);
        ec.extract (cluster_indices);
        
        int j = 0;
        for (std::vector<pcl::PointIndices>::const_iterator it = cluster_indices.begin (); it != cluster_indices.end (); ++it)
        {
            pcl::PointCloud<pcl::PointXYZ>::Ptr cloud_cluster (new pcl::PointCloud<pcl::PointXYZ>);
            
            for (std::vector<int>::const_iterator pit = it->indices.begin (); pit != it->indices.end (); ++pit)
                cloud_cluster->points.push_back (cloud_filtered->points[*pit]); //*

            cloud_cluster->width = cloud_cluster->points.size ();
            cloud_cluster->height = 1;
            cloud_cluster->is_dense = true;

            f_log << "    * " << label_to_string_sem3d.at(i_pc_array) << "_" << j << " [size]:" << cloud_cluster->points.size () << std::endl;
            std::cout << "    * " << label_to_string_sem3d.at(i_pc_array) << "_" << j << " [size]:" << cloud_cluster->points.size () << std::endl;
            
            std::stringstream ss;
            ss << cluster_folder_path << "/" << label_to_string_sem3d.at(i_pc_array) << "_" << j << ".pcd";
            writer.write<pcl::PointXYZ> (ss.str(), *cloud_cluster, false); //*
            j++;
        }
        
        point_cloud_ptr_array.at(i_pc_array)->clear();
        f_log << boost::format("  - Execution time for clustering[%1%]: %2%") % label_to_string_sem3d.at(i_pc_array) % ((double)(clock() - tStart)/CLOCKS_PER_SEC) << std::endl;
        std::cout << boost::format("  - Execution time for clustering[%1%]: %2%") % label_to_string_sem3d.at(i_pc_array) % ((double)(clock() - tStart)/CLOCKS_PER_SEC) << std::endl;
    }

    std::cout << "End clustering" << std::endl;


    f_log.close();
    f_data.close();
    f_label.close();

    return (0);
}

