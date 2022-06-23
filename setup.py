from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'USGS Lidar package'
LONG_DESCRIPTION = '...'

# Setting up
setup(
       
        name="usgs_lidar_lib", 
        version=VERSION,
        author="Yonas Tadesse Zinaye",
        author_email="<yonaztad@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. 
        
        keywords=['python', 'lidar', 'usgs', 'agri tech'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)