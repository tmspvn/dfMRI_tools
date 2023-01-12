import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from matplotlib.patches import Rectangle

def print_volume(data: np.ndarray, time:int=15) -> None:
    """"
    Function that prints an overview of the z slices, at a fixed time=b-val
    
    Args:
        data (np.ndarray) : data to plot
        time (int) : time or b-value at which to plot the data 
    
    """

    nrows = 2
    ncols = int(data.shape[2]/nrows)
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols,figsize=(10, 5))

    for i in range(data.shape[2]):
        if data.ndim == 4:
            slice = data[:, :, i,time]
        elif data.ndim == 3:
            slice = data[...,i]
        ax[i//ncols][i%ncols].imshow(slice.T, cmap="gray", origin="lower")

def plot_timeserie_byepoch(timeserie_by_epoch: np.ndarray, annotation_type: str) -> None:
    """
    Function that plots the mean timeserie over one epoch.
    
    Args:
        timeserie_by_epoch (np.ndarray): timeserie, grouped by epoch,
                                         (number_of_epoch x epoch_length)
        annotation_type (str) : type of annotation of the plot. Either "STD" or "CI", to
                                plot the standard deviation or the 95% CI, respectively.
    
    """
    x = np.arange(0, 30, 2)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    mean = np.mean(timeserie_by_epoch, axis=0)

    assert np.isin(annotation_type,["STD", "CI"]), "Annotation_type should be either 'STD' or 'CT'!" 
    
    if annotation_type == "STD":
        std = np.std(timeserie_by_epoch, axis=0)
        y_max = max(mean+std) + 0.0001
        y_min = min(mean-std)
        ax.errorbar(x, mean, std, fmt='-o', color='k')
    elif annotation_type == "CI":
        CI_low, CI_high = st.t.interval(alpha=0.95, df=timeserie_by_epoch.shape[0]-1, 
                      loc=np.mean(timeserie_by_epoch, axis=0), 
                      scale=st.sem(timeserie_by_epoch, axis=0))
        y_max = max(CI_high)
        y_min = min(CI_low)
        ax.plot(x, mean)
        ax.fill_between(x, CI_low, CI_high, color='blue', alpha=0.1)
  
    ax.axhline(y = 1, color = 'k', linestyle = '--')
    x_annotation = 5
    y_annotation = y_max
    ax.annotate('Stim on', (x_annotation,y_annotation))
    ax.add_patch(Rectangle((0, y_min), 12, y_max - y_min, facecolor='darkgray', alpha=0.5))
    x_annotation = 19
    ax.annotate('Stim off', (x_annotation,y_annotation))
    ax.add_patch(Rectangle((12, y_min), 18, y_max - y_min, alpha=0.1))
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('ADC relative to baseline + ' + annotation_type)
    plt.show()