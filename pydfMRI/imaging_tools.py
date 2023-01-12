import numpy as np
import nibabel as nib

def calculate_temporal_mean(input_img: np.ndarray) -> float:
    """
    Calculate the temporal mean of a 4D image
    
    Args:
        input_img (np.ndarray) : 4D volume
    
    Returns:
        (np.ndarray) :3D volume, averaged w.r.t. time axis
    
    """

    return np.mean(input_img, axis=3)

def calculate_temporal_std(input_img: np.ndarray) -> float:
    """
    Calculate the temporal standard deviation of a 4D image
    
    Args:
        input_img (np.ndarray): 4D volume
    
    Returns:
        (np.ndarray): 3D volume, standard deviation w.r.t. time axis
    
    """

    return np.std(input_img, axis=3)

def calculate_temporal_snr(input_img: np.ndarray, TR: float) -> np.ndarray:
    """
    Calculate the temporal SNR of a 2D image
    
    Args:
        input_img (np.ndarray) : 2D volume
        TR (float): repetition time [ms]
   
    Returns:
        (np.ndarray): SNR w.r.t. time axis
    
    """

    tmean_img = calculate_temporal_mean(input_img)
    tstd_img = calculate_temporal_std(input_img)
    tSNR = tmean_img / (tstd_img*np.sqrt(TR))
    return tSNR

def find_significant_vx(mask_name: str, mask_idx: list, zfmap_name: str, thresh: float=3.1) -> np.ndarray:
    """
    Function that finds the significant ADC voxels, based on SPM GLM analysis
    
    Args:
        mask_name (str) : name of the mask used. "mask_VOI_{zone}_subject_space.nii.gz", 
                          zone = ["all", "motor", "somatosensori", "visual"]
        mask_idx (list) : mask indices of interest
        zfmap_name (str) : name of the F to z statistical map
        thresh (float) : threshold for significance

    Returns:
        significant_vx (np.ndaray) : array of x,y,z indices of significant voxel
    
    """

    mask: np.ndarray = nib.load(mask_name)
    mask = mask.get_fdata()

    zscore = nib.load(zfmap_name)
    zscore = zscore.get_fdata()

    significant_vx = np.argwhere(np.isin(mask, mask_idx) & (zscore > thresh))

    del mask, zscore
    
    return  significant_vx

def load_adc_timecourses(adc_filename: str, significant_vx: np.ndarray) -> np.ndarray:
    """
    Function that loads the ADC timeseries of the significant voxels
   
    Args:
        adc_filename (str) : filename where adc.nii.gz is stored
        significant_vx (np.ndarray) : array containing the x,y,z indices of the 
                                      significant ADC voxels
   
    Returns:
        (np.ndarray) : (len(significant_vx) x adc.shape[3])
    
    """

    adc = nib.load(adc_filename)
    adc = adc.get_fdata()
    adc_timecourses = np.zeros((len(significant_vx), adc.shape[3]))

    for i in range(len(significant_vx)):
        adc_timecourses[i, :] = adc[significant_vx[i][0], significant_vx[i][1], significant_vx[i][2], :]

    del adc

    return adc_timecourses

def reshape_timeseries_byepoch(timeserie: np.ndarray, epoch_length: int=15) -> np.ndarray:
    """
    Function that reshape a timeserie from [epoch1, epoch2, ..., epochn] to 
    [epoch1,
    epoch2,
    ...,
    epochn].
    If the length of timeserie is not a multiple of epoch_length, discard the first rest
    values of the timeserie.

    Args:
        timeserie (np.ndarray): timeserie to reshape
        epoch_length (int): duration of "1 epoch in [s] divided by TR"
    
    Returns:
        (np.ndarray): array of size (number_of_epochs, epoch_length)
    
    """

    epochs_to_discard = timeserie.shape[0] % epoch_length
    adc_timecourse = timeserie[epochs_to_discard:]

    return adc_timecourse.reshape((-1, epoch_length))

def normalize_epoch(timeserie_by_epoch: np.ndarray, baseline_length: int=5) -> np.ndarray:
    """
    Function that normalizes the ADC timeserie groubed by epoch with
    the last baseline_length values of each epoch.
    
    Args:
        timeserie_by_epoch (np.ndarray) : timeserie, grouped by epoch 
                                          (number_of_epoch x epoch_length)
        baseline_length (int) : takes the last baseline_length samples to calculate the 
                                baseline
    
    Returns:
        timeserie_by_epoch (np.ndarray) : normalized timeserie, grouped by epoch
                                          (number_of_epoch x epoch_length)
    
    """

    for i in range(timeserie_by_epoch.shape[0]):
        # Takes the last sample of an epoch to calculate the baseline  
        baseline_adc = np.mean(timeserie_by_epoch[i,-baseline_length:])
        timeserie_by_epoch[i,:] = timeserie_by_epoch[i,:]/baseline_adc

    return timeserie_by_epoch