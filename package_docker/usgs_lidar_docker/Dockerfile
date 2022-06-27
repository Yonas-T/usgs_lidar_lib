FROM python:3.10
RUN conda create -n usgslidarlib && conda activate usgslidarlib && conda install -c conda-forge pdal python-pdal gdal && conda install pip && pip install requirements.txt && pip install UsgsLidarLib
