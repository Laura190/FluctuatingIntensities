#!/usr/bin/env python
# coding: utf-8

# # Fluctuating Intensities
# ## Read files from OMERO and analyse fluctuations of pixel intensities
# ### Laura Cooper 29/05/2020

# ## Prerequisites
# This notebook assumes the default group for the user in OMERO is Royle-Cooper and that you are connected to the VPN.
# ### Import Packages

# In[105]:


from omero.gateway import BlitzGateway
import getpass
import numpy as np
from scipy import fft, ndimage
import matplotlib.pyplot as plt
import csv
from RetrieveCred import passwd, usernm


# ### Define functions
# #### Convert image stack to np.array

# In[2]:


def get_z_stack(img, c=0, t=0):
    """
    Convert OMERO image object to numpy array
    Input: img  OMERO image object
           c    number of colour channls
           t    number of time steps
    """
    zct_list = [(z, c, t) for z in range(img.getSizeZ())] #Set dimensions of image
    pixels = img.getPrimaryPixels()
    return np.array(list(pixels.getPlanes(zct_list))) #Read in data one plane at a time


# #### Calculate turbulence statistics

# In[3]:


def turb_stats(f, Fs):
    """
    Get turblence statistics for each pixel
    Input: f     numpy array of image
           Fs    sample frequency
    """
    L=np.shape(f)
    # mean velocity over time for every pixel
    ind_u_bar=np.mean(f, axis = 0); #mean over time
    # Reynolds decomposition to calculate turbulent fluctuations
    ind_u_fluct=np.subtract(f,ind_u_bar)
    #Turblence Strength
    ind_u_rms=np.std(ind_u_fluct, axis = 0) #standard deviation over time
    # Frequency spectrum
    ind_u_fft=fft.fft(ind_u_fluct, axis = 0) #fast fourier transform in time
    P2=abs(ind_u_fft/L[0]) #2 sided spectrum
    P1=P2[0:int(L[0]/2)]; #1 sided spectrum
    P1[1:len(P1)-1]=2*P1[1:len(P1)-1];
    fd=Fs*np.arange(0,L[0]/2,1)/L[0]; #Freqency domain
    return ind_u_bar, ind_u_rms, P1, fd


# I have named the variables here as they would be called in a turbulence study (as this is want makes sense to me). To relate them to the current problem:
# - Mean velocity is mean intensity
# - Turbulent fluctuations are intensity flucuations
# - Turblence Strength is the standard deviation of the set of intensity fluctuations

# #### Calculate tubulence statistics for all images in a dataset

# In[4]:


def Fluc_ds(dataset):
    """
    Get mean turblence statistics for each image in dataset
    Input: dataset     OMERO dataset object
    """
    # define arrays results
    # 16 is the number of images in each data set.
    # 15 is half the number of time steps
    u_bar = np.zeros(16) #mean velocity
    u_rms = np.zeros(16) #turbulence strength
    P1_mean = np.zeros([15,16]) #Amplitude of signal
    fd_all = np.zeros([15,16]) #Frequency of signal
    Iid = np.zeros(16, dtype=int) #Image IDs for referring back to OMERO
    i=0;
    for image in conn.getObjects('Image', opts={'dataset': dataset}): #loop all images in data set
        Iid[i] = image.getId()
        f = get_z_stack(image)
        ind_u_bar, ind_u_rms, P1, fd = turb_stats(f, 5.6) #Assumes sample frequency same for all images
        #Average in space         
        u_bar[i]=np.mean(ind_u_bar, axis=(0,1))
        u_rms[i] = np.mean(ind_u_rms, axis=(0,1))
        P1_mean[:,i]=np.mean(P1,axis=(1,2))
        fd_all[:,i]=fd
        i=i+1
    return Iid, u_bar, u_rms, P1_mean, fd_all


# #### Write dictionary to file

# In[180]:


def dict2csv(dictionary, filename):
    """
    write dictionary to csv file
    Input: dictionary     A dictionary 
           filename       name of output file
    """
    dict = dictionary;
    w = csv.writer(open(filename, "w"))
    for key, val in dict.items():
        w.writerow([key, val])


# #### Read dictionary from file

# In[187]:


def csv2dict(filename):
    """
    write dictionary to csv file
    Input: filename       name of input file
    """
    with open (filename, "r", newline='\n') as csvfile:
        csv_reader=csv.reader(csvfile,delimiter=',')
        dictionary={}
        for row in csv_reader:
            k=row[0]
            v=row[1]
            v=v.replace('[','')
            v=v.replace(']','')
            dictionary[k]=np.fromstring(v,sep=' ')
    return dictionary


# ## Method
# ### Connect to OMERO

# In[5]:


conn = BlitzGateway(usernm, passwd, host='camdu.warwick.ac.uk', port=4064)
conn.connect() #Returns true when connected


# ### Get OMERO IDs
# List the details of the datasets we are interested in from OMERO. We need the IDs to call the images we want to analyse. The output allows us to identify the relevant datasets.

# In[6]:


print("\nList Datasets: \n", "=" * 50)
datasets = conn.getObjects("Dataset", opts={'owner': 3}) #get all datasets from owner 3 (SR)
keys=[] #create empty lists
values=[]
for obj in datasets:
    print("""%s%s:%s  Name:"%s" (owner=%s)""" % (
        " " * 2,
        obj.OMERO_CLASS,
        obj.getId(),
        obj.getName(),
        obj.getOwnerOmeName()
    ))
    keys.append(obj.getName()) #gather dataset names to use in dictionary
    values.append(obj.getId()) #gather dataset IDs to use in dictionary


# Put names and IDs in dictionary to make it easy to call required datasets.

# In[7]:


Datasets=dict(zip(keys[:-1], values[:-1]))


# Set up dictionarys for results using the same names as the datasets. _Im here means these are the mean results for each image

# In[8]:


ImageIDs=dict.fromkeys(keys[:-1])
Mean_Vel_Im=dict.fromkeys(keys[:-1])
TurbStreng_Im=dict.fromkeys(keys[:-1])
Amp_Im=dict.fromkeys(keys[:-1])
Freq_Im=dict.fromkeys(keys[:-1])


# For each dataset calculate the turbulence statistics for every image

# In[9]:


for key in Datasets:
    ImageIDs[key], Mean_Vel_Im[key], TurbStreng_Im[key], Amp_Im[key], Freq_Im[key] = Fluc_ds(Datasets[key])


# Close connection to OMERO

# In[10]:


conn.close()


# ## Results
# Every image in stack

# In[23]:


fig, axs = plt.subplots(2,3,figsize=(20,10))
fig.add_subplot(111, frameon=False)
for key in Datasets:
    axs[int(list(Datasets.keys()).index(key)>=3),list(Datasets.keys()).index(key)%3].plot(Freq_Im[key],Amp_Im[key])
    axs[int(list(Datasets.keys()).index(key)>=3),list(Datasets.keys()).index(key)%3].title.set_text(key)

# hide tick and tick label of the big axes
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
plt.grid(False)
plt.xlabel("Frequency",fontsize = 20)
plt.ylabel("Relative Amplitude",fontsize = 20)
plt.title("Frequency Spectra for Individual Images in Datasets",fontsize = 20,pad=40)
plt.show;
fig.savefig('EveryImageFreqSpec.png',transparent=True);


# For each dataset, the frequency spectrum of each image is plotted. Note that the y axis are different. INV and recycling endosomes show much higher amplitudes than the other four datasets, i.e. they have larger changes in intensity. I was hoping the graphs would show different peaks. This would indicate that the pixel intensitites were fluctuating a different speeds. To find out, the analysis needs to be run for more time steps.
# 
# The mean values for each dataset are also found and plotted

# In[24]:


Amp_meanDS=dict.fromkeys(keys[:-1])
Freq_meanDS=dict.fromkeys(keys[:-1])
Amp_stdDS=dict.fromkeys(keys[:-1])
Mean_Vel_DS=dict.fromkeys(keys[:-1])
TurbStreng_DS=dict.fromkeys(keys[:-1])
for key in Amp_meanDS:
    Amp_meanDS[key]=np.mean(Amp_Im[key], axis=1)
    Freq_meanDS[key]=np.mean(Freq_Im[key], axis=1)
    Amp_stdDS[key]=np.std(Amp_Im[key], axis=1)
    Mean_Vel_DS[key]=np.mean(Mean_Vel_Im[key])
    TurbStreng_DS[key]=np.mean(TurbStreng_Im[key])


# In[25]:


fig, axs = plt.subplots(2,3,figsize=(20,10),sharey=True)
fig.add_subplot(111, frameon=False)
for key in Datasets:
    axs[int(list(Datasets.keys()).index(key)>=3),list(Datasets.keys()).index(key)%3].plot(Freq_meanDS[key],Amp_meanDS[key])
    axs[int(list(Datasets.keys()).index(key)>=3),list(Datasets.keys()).index(key)%3].fill_between(Freq_meanDS[key], Amp_meanDS[key]-Amp_stdDS[key], Amp_meanDS[key]+Amp_stdDS[key] ,alpha=0.3)
    axs[int(list(Datasets.keys()).index(key)>=3),list(Datasets.keys()).index(key)%3].title.set_text(key)
plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
plt.grid(False)
plt.xlabel("Frequency",fontsize = 20)
plt.ylabel("Relative Amplitude",fontsize = 20)
plt.title("Frequency Spectra for Mean of Datasets",fontsize = 20,pad=40)
plt.show;
fig.savefig('MeanImageFreqSpec.png',transparent=True);


# Here the mean frequency spectrum of each data set is shown. The y-axes are all the same to emphasis the differences in the amplitude. The shaded area shows $\pm$ 1 standard deviation from the mean.
# 
# The mean intensity of the pixels in each image are shown below.

# In[26]:


fig, ax = plt.subplots(figsize=(12,7))
ax.bar(np.arange(len(list(Mean_Vel_DS.values()))), list(Mean_Vel_DS.values()), yerr=list(TurbStreng_DS.values()), align='center', alpha=0.5, ecolor='black', capsize=10)
ax.set_ylabel('Mean Pixel Intensity',fontsize=20)
ax.set_xticks(np.arange(len(list(Mean_Vel_DS.values()))))
ax.set_xticklabels(Mean_Vel_DS.keys(), fontsize=12)
ax.set_title('Mean Pixel Intensity of Each Dataset',fontsize=20)
fig.tight_layout()
plt.show()
fig.savefig('MeanIntensity.png');


# The error bars show the $\pm$ 1 root mean square of the fluctuations.

# In[191]:


dict2csv(Mean_Vel_DS, 'Mean_Vel_DS.csv')
dict2csv(TurbStreng_DS, 'TurbStreng_DS.csv')
dict2csv(Amp_meanDS, 'Amp_meanDS.csv')
dict2csv(Freq_meanDS, 'Freq_meanDS.csv')


# In[ ]:




