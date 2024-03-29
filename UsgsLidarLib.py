from shapely.geometry import box, Point, Polygon
import geopandas as gpd
import matplotlib.pyplot as plt
import pickle
import os
import pandas as pd
import numpy as np

from scripts.load_data import LoadData
from scripts.utils import *
from scripts.subsample import *


from scripts.dataframe_constructor import DataframeConstructor


class UsgsLidarLib:
    """This is a class for fetching, manipulating, and visualizing point cloud data. The package will accept boundary polygons in shapely.geometry.Polygon, and a coordinate reference system (CRS) and return a python dictionary with all years of data available and a geopandas grid point file with elevations encoded in the requested CRS.
     The package will also provide an option to graphically display the returned elevation files as a 3D plot and 2D heatmap.
    """

    def __init__(self, crs_epsg: int) -> None:
        """This method is used to instantiate the class. It takes a CRS EPSG value (i.e refer to https://epsg.io/) to use.
        Args:
            crs_epsg (int): an integer EPSG value of coordinate reference system
        """

        try:
            self.meta_data = pd.read_csv("../data/metadata.csv")
            print(self.meta_data)
            self.meta_data['year'] = self.meta_data['year'].fillna(0)
            self.meta_data['year'] = self.meta_data['year'].astype('int')
        except:
            print("Could not read a metadata file")

        self.epsg = crs_epsg
        self.fetcher = LoadData()
        self.ee = DataframeConstructor()

    def __get_region_from_boundary(self, bounds) -> gpd.GeoDataFrame:
        """This method accepts a Boundaries object which defines xmin, ymin, xmax, ymax and returns a dataframe of regions containing the boundary provieded.
        Args:
            bounds (Boundaries): a Boundaries object which defines a bound in form of xmin, ymin, xmax, ymax
        Returns:
            geopandas.GeoDataFrame: a dataframe containing rows of region name, filename location and year of the could point dataset containing the boundary defined 
        """
        print(bounds)
        filtered_df = self.meta_data.loc[
            (self.meta_data['xmin'] <= bounds['minx'])
            & (self.meta_data['xmax'] >= bounds['maxx'])
            & (self.meta_data['ymin'] <= bounds['miny'])
            & (self.meta_data['ymax'] >= bounds['maxy'])
        ]
        return filtered_df[["filename", "region", "year"]]

    def __get_regions(self, polygon: Polygon) -> dict:
        """This metods accepts a boundary polygon finds all region file names and years containing the boundary polygon.
        Args:
            polygon (Polygon): shapely.geometry.Polygon object defining a boundary polygon
        Returns:
            dict: a dictionary where the keys are year and the values are region file names for all region containg the boundary polygon.
        """
        polygon_df = gpd.GeoDataFrame([polygon], columns=['geometry'])

        polygon_df.set_crs(epsg=4326, inplace=True)
        polygon_df['geometry'] = polygon_df['geometry'].to_crs(
            epsg=3857)

        minx, miny, maxx, maxy = polygon_df['geometry'][0].bounds

        # bounds = ([minx, miny], [maxy, maxx])
        bounds = {
            'minx': minx,
            'miny': miny,
            'maxy': maxy,
            'maxx': maxx
        }

        filtred_df = self.__get_region_from_boundary(bounds)
        filenames = filtred_df['filename'].to_list()
        years = filtred_df['year'].to_list()

        filename_year = dict()

        for filename, year in zip(filenames, years):
            filename_year[year] = filename

        return filename_year
    
   

    def get_elevation_df(self, polygon: Polygon, from_cache=False, enforce_cache=False) -> dict:
        """This method accepts a boundary polygon and returns a Python dictionary with all years of data available and geopandas grid point file with elevations encoded in the requested CRS of this object. The requested CRS is provided in the class init step.
        Args:
            polygon (Polygon): shapely.geometry.Polygon object defining a boundary polygon
            from_cache (bool, optional): if this value is true, it will first look  the result from the local cache file based on the queried polygon boundary. Defaults to False.
            enforce_cache (bool, optional): if this value is true, the result is going to be cahced in local file. Defaults to False.
        Returns:
            dict: a Python dictionary where the keys area all years of data available  and values are  geopandas grid point file with elevations encoded in the requested CRS of this object
        """

        result = dict()

        cache_file_name = get_cache_name_from_polygon(polygon)

        if (from_cache and os.path.isfile(cache_file_name)):
            return read_obj(cache_file_name)

        regions_year_dict = self.__get_regions(polygon)

        ind = 0

        for year in regions_year_dict:

            file_name = regions_year_dict[year]
            if year == 0:
                year = "Unknown"

            try:
                print(
                    f"trying to Fetch elevation data for year {year} from file_name {file_name}...")

                data, output_epsg = self.fetcher.runPipeline(
                    file_name, polygon)
                df = self.ee.get_elevetion(data)
                result[year] = df
            except:
                pass
            ind += 1

        if enforce_cache:
            cache_fetched_data(cache_file_name, result)

        return result

    def save_elevation_geodata(self, df: gpd.GeoDataFrame,  file_name: str, save_format="shp"):
        """This method saves a geopandas dataframe containing elevation points.
        Args:
            df (geopandas.GeoDataFrame): a geopandas data frame to be saved, the dataframe must contain int sereis cloumn called elevation and and a geometry point series column called geometry.
            file_name (str): the name of the file to be saved. 
            save_format (str, optional): the formats to be used to save the dataframe, two format options are supported, 'shp' and 'geojson'. Defaults to "shp".
        """

        #         polygon_df = gpd.GeoDataFrame([polygon], columns=['geometry'])
        #         polygon_df.set_crs(epsg=self.epsg, inplace=True)

        if save_format == "shp":
            df.to_file(f"{file_name}.shp")

        elif save_format == "geojson":
            df.to_file(f"{file_name}.geojson", driver='GeoJSON')

        else:
            print("Unsupported format, geojson and shp are only supported formats")

    def get_heatmap_visulazation(self, df: gpd.GeoDataFrame, cmap="terrain") -> None:
        """Plots a 2D heat map for the cloud datapoints of geopandas dataframe using matplotlib
        Args:
            df (geopandas.GeoDataFrame): a geopandas data frame,  the dataframe must contain int sereis cloumn called elevation and and a geometry point series column called geometry.
            cmap (str, optional): color map for the heatmap (i.e refer to https://matplotlib.org/stable/gallery/color/colormap_reference.html). Defaults to "terrain".
        """

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        df.plot(column='elevation', ax=ax, legend=True, cmap=cmap)
        plt.show()

    def get_3D_visualzation(self, df, s=0.01, color="blue"):
        """Plots a 3D terrain scatter plot for the cloud datapoints of geopandas dataframe using matplotlib
        Args:
            df (geopandas.GeoDataFrame): a geopandas data frame,  the dataframe must contain int sereis cloumn called elevation and and a geometry point series column called geometry.
            s (float, optional): S value. Defaults to 0.01.
            color (str, optional): color of the points. Defaults to "blue".
        """

        x = df.geometry.x
        y = df.geometry.y
        z = df.elevation

        points = np.vstack((x, y, z)).transpose()

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        ax = plt.axes(projection='3d')
        ax.scatter(points[:, 0], points[:, 1],
                   points[:, 2],  s=0.01, color="blue")
        plt.show()

    def subsampling_interpolation(self, df: gpd.GeoDataFrame, resolution: int):
        """This method  accepts a geopandas dataframe and a resoultion and implements sub-sampling methods for reducing point cloud data density using grid system.
        Args:
            df (geopandas.GeoDataFrame): a geopandas data frame,  the dataframe must contain int sereis cloumn called elevation and and a geometry point series column called geometry.
            resolution (int): The resolution defines the grid area (in meter square) which a single point represents. 
        Returns:
            geopandas.GeoDataFrame: a subsampled interpolated geopandas dataframe
        """
        df_meter = df.copy()
        df_meter['geometry'] = df_meter.geometry.to_crs(32643)
        df_meter = df_meter.set_crs(epsg=32643)

        subsample_df = subsample.grid_barycenter_sample(df_meter, resolution)
        print(f"subsampled number of points {subsample_df.shape[0]}")
        return subsample_df

    def covert_crs(self, df: gpd.GeoDataFrame, crs_epgs: int) -> gpd.GeoDataFrame:
        """This method accepts a geopandas dataframe and a CRS and converts the dataframe to the provided coordinate reference system
        Args:
            df (geopandas.GeoDataFrame): a geopandas data frame,  the dataframe must contain int sereis cloumn called elevation and and a geometry point series column called geometry.
            crs_epgs (int): [description]
        Returns:
            geopandas.GeoDataFrame: an integer EPSG value of coordinate reference system, (i.e refer to https://epsg.io/)
        """

        return self.ee.covert_crs(crs_epgs, df)