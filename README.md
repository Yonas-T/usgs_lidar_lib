<div id="top"></div>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  

  <h3 align="center">Agritech USGS LIDAR Python Package</h3>

</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

usgs_lidar_lib is an open-source python package for retrieving, transforming, and visualizing point cloud data obtained through an aerial LiDAR survey. The package will accept boundary polygons and a coordinate reference system (CRS) and return a python dictionary with all years of data available and a geopandas grid point file with elevations encoded in the requested CRS. 


### Built With

This project is built mainly with the following python libraries.

1. Pdal
2. laspy
3. Geopandas
4. pandas


### Prerequisites

Creating a conda environment
* conda
  ```sh
  conda create -n <your environment name>
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Yonas-T/usgs_lidar_lib.git
   ```
2. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```


<!-- CONTACT -->
## Contact

Yonas Tadesse - (https://www.linkedin.com/in/yonastadessezin/) - yonaztad@gmail.com


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments


* [PDAL](https://pdal.io/)
