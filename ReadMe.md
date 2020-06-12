## FluctuatingIntensities
Investigate the fluctuation of intensities of subresolution pixels from cell imaging (SR)

#Files:
FluctuatingIntensities_TestingAndValidation.ipynb  
Jupyter notebook: For testing things out and checking they work

FluctuatingIntensities.ipynb  
Jupyter notebook: Calculates mean velocity, standard deviation and frequency spectra of all images in all datasets and plots some results

FlucInte.yml  
Conda environment file: For creating and activating a conda environment that contains the required packages for FluctuatingIntensities.ipynb and FluctuatingIntensities_TestingAndValidation.ipynb. To create the environment run the command
$ conda env create -f FlucInte.yml

FluctuatingIntensities.py  
Python script that has the same output as the Jupyter notebook, but saves to external files and can be run on the CoW  
Requires python virtual environment called FlucInte with packages omero-py==5.6.9 cryptography and scikit-image

RetrieveCred.py
Python script required for running FluctuatingIntensitites.py