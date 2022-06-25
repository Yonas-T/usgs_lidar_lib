from shapely.geometry import box, Point, Polygon
import pandas as pd
import os
import pickle

cache_folder = "./cache"


def read_obj(file_name):
    with open(f"{cache_folder}/{file_name}.pkl", "rb") as f:
        return pickle.load(f)


def write_obj(file_name, obj):
    if (not os.path.isdir('./cache')):
        os.mkdir("./cache/")

    with open(f"{cache_folder}/{file_name}.pkl", "wb") as f:
        pickle.dump(obj, f)


def get_cache_name_from_polygon(polygon: Polygon):
    """This method generates a unique cache name by hashing a query polygon coordinate points
    Args:
        polygon (Polygon): shapely.geometry.Polygon object defining a boundary polygon
    Returns:
        str: a unique cache name for a query polygon
    """
    x, y = polygon.exterior.coords.xy

    temp = ""
    for i, j in zip(list(x), list(y)):
        temp += f"{i}_{j}"

    hashed_name = hash(temp)

    if hashed_name < 0:
        hashed_name = "a" + str(hashed_name)[1:]

    return hashed_name


def cache_fetched_data(file_name: str, obj):

    try:
        write_obj(str(file_name), obj)
    except:
        pass