import os
import json
import pdal
import geopandas as gpd
from shapely.geometry import Polygon, Point

class LoadData:
    def __init__(self) -> None:
        self.input_epsg = 3857
        self.output_epsg = 26915
        self.__createDataFolderStruct()
        

    def __readFetchJson(self, path: str) -> dict:
        """This method reads json file using python json lib.
        Args:
            path (str): path for the json file
        Returns:
            dict: a dictionary object of the parsed json file
        """
        try:
            with open(path, 'r') as json_file:
                dict_obj = json.load(json_file)
            return dict_obj

        except FileNotFoundError as e:
            print('Json File Not Found')
    
    def get_polygon_boundaries(self, polygon: Polygon) -> tuple:
        """This method is used to calculate rectangular bounds of a given polygon and returns a string representation of the calculated bounds in a '({[minx, maxx]},{[miny,maxy]})' format (i.e the format our pdal pipeline's reader.ept (https://pdal.io/stages/readers.ept.html#readers-ept) expects. example ([-8242669, -8242529], [4966549, 4966674])).
        It also returns a string format of the given polygon in a format that pdal pipeline's  filters.crop opreation expects. i.e POLYGON((0 0, 5000 10000, 10000 0, 0 0))
        Args:
            polygon (Polygon): a given shapely.geometry.Polygon object
        Returns:
            tuple: returns a 2 element tuple in which the first is  a string representation of the calculated bounds in a '({[minx, maxx]},{[miny,maxy]})' format and the second is a string format of the given polygon in a format that pdal pipeline's  filters.crop opreation expects. i.e POLYGON((0 0, 5000 10000, 10000 0, 0 0))
        """
        polygon_df = gpd.GeoDataFrame([polygon], columns=['geometry'])

        polygon_df.set_crs(epsg=self.output_epsg, inplace=True)
        polygon_df['geometry'] = polygon_df['geometry'].to_crs(
            epsg=self.input_epsg)

        minx, miny, maxx, maxy = polygon_df['geometry'][0].bounds

        polygon_input = 'POLYGON(('

        xcord, ycord = polygon_df['geometry'][0].exterior.coords.xy
        for x, y in zip(list(xcord), list(ycord)):
            polygon_input += f'{x} {y}, '
        polygon_input = polygon_input[:-2]
        polygon_input += '))'

        return f"({[minx, maxx]},{[miny,maxy]})", polygon_input

    def getPipeline(self, region: str, polygon: Polygon):
        """This method prepares our fetching pipeline using by using pipeline json description found in the root directory of the package. 
        Args:
            region (str): the region defines the region  point cloud data resource. 
            polygon (Polygon): the polygon  is a shapely.geometry.Polygon object which defines the boundaries of our cloud data points to be fetched
        Returns:
            pdal.Pipeline: returns a prepared pdal pipeline object
        """

        public_data_url = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/"
        
        fetch_json_path="../fetch.json"
        fetch_json = self.__readFetchJson(fetch_json_path)

        boundaries, polygon_input = self.get_polygon_boundaries(polygon)

        full_dataset_path = f"{public_data_url}{region}/ept.json"

        fetch_json['pipeline'][0]['filename'] = full_dataset_path
        fetch_json['pipeline'][0]['bounds'] = boundaries

        fetch_json['pipeline'][1]['polygon'] = polygon_input

        fetch_json['pipeline'][6]['out_srs'] = f'EPSG:{self.output_epsg}'


        pipeline = pdal.Pipeline(json.dumps(fetch_json))

        return pipeline

    def runPipeline(self, region: str, polygon: Polygon):
        """reads the point cloud data from the EPT resource on AWS. We give it a region and a boundary polygon.
        Args:
            region (str): region of the cloud data EPT resource 
            polygon (Polygon): a shapely.geometry.Polygon object which defines the boundaries of our cloud data points to be fetched.
        Returns:
            list: it returns a list of a numpy array of cloud point data 
        """
        pipeline = self.getPipeline(region, polygon)

        try:
            pipeline.execute()
            metadata = pipeline.metadata
            log = pipeline.log
            return pipeline.arrays, self.output_epsg
        except RuntimeError as e:
            print(e)

    def __createDataFolderStruct(self):
        """This method creates a data/laz and data/tif dir if not exist
        """
        if (not os.path.isdir('./data')):
            os.mkdir("./data")
            os.mkdir("./data/laz/")
            os.mkdir("./data/tif/")
        if (not os.path.isdir('./data/laz')):
            os.mkdir("./data/laz/")
        if (not os.path.isdir('./data/tif')):
            os.mkdir("./data/tif/")
