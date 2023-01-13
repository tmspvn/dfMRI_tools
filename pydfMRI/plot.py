import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from matplotlib.patches import Rectangle
from scipy.ndimage import zoom
import imageio
import nibabel as nib


def print_volume(data: np.ndarray, time: int = 15) -> None:
    """"
    Function that prints an overview of the z slices, at a fixed time=b-val
    
    Args:
        data (np.ndarray) : data to plot
        time (int) : time or b-value at which to plot the data 
    
    """

    nrows = 2
    ncols = int(data.shape[2] / nrows)
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, 5))

    for i in range(data.shape[2]):
        if data.ndim == 4:
            slice = data[:, :, i, time]
        elif data.ndim == 3:
            slice = data[..., i]
        ax[i // ncols][i % ncols].imshow(slice.T, cmap="gray", origin="lower")


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

    assert np.isin(annotation_type, ["STD", "CI"]), "Annotation_type should be either 'STD' or 'CT'!"

    if annotation_type == "STD":
        std = np.std(timeserie_by_epoch, axis=0)
        y_max = max(mean + std) + 0.0001
        y_min = min(mean - std)
        ax.errorbar(x, mean, std, fmt='-o', color='k')
    elif annotation_type == "CI":
        CI_low, CI_high = st.t.interval(alpha=0.95, df=timeserie_by_epoch.shape[0] - 1,
                                        loc=np.mean(timeserie_by_epoch, axis=0),
                                        scale=st.sem(timeserie_by_epoch, axis=0))
        y_max = max(CI_high)
        y_min = min(CI_low)
        ax.plot(x, mean)
        ax.fill_between(x, CI_low, CI_high, color='blue', alpha=0.1)

    ax.axhline(y=1, color='k', linestyle='--')
    x_annotation = 5
    y_annotation = y_max
    ax.annotate('Stim on', (x_annotation, y_annotation))
    ax.add_patch(Rectangle((0, y_min), 12, y_max - y_min, facecolor='darkgray', alpha=0.5))
    x_annotation = 19
    ax.annotate('Stim off', (x_annotation, y_annotation))
    ax.add_patch(Rectangle((12, y_min), 18, y_max - y_min, alpha=0.1))
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('ADC relative to baseline + ' + annotation_type)
    plt.show()


def mkgif(img, path=False, view=0, slice4d=False, rotate=False, rotaxes=(1, 2), flip=False, rewind=True,
          winsorize=[1, 98],
          timebar=True, crosshair=False, scale=2, cmap=False, crop=True, vol_wise_norm=False, fps=60, concat_along=1):
    """
    Make gif from nifti images.

    Args:
        img: one or more image filepaths, nibNifti1Images or ndarrays
        path: string, filename to save the .gif. if False use input filename. [default=False]
        view: string or bool, specify type of view to plot: 'sagittal' or 0 [Default], 'coronal' or 1, 'axial' or 2
        rewind: bool, repeat the animation backwards. [default:=True]
        winsorize: list, winsorize image intensities to remove extreame values. [default:=[1,98]]
        rotaxes: tuple, axis along which rotate the image. [default=(1, 2)]
        rotate: int [1:3], int*90-degree rotation counter-clockwise. [default=False]
        slice4d: int: index where to slice chosen view in 4D image. [default=False -> img.shape[1]//2]
        timebar: bool, print timebar at the bottom [default=True]
        flip: int, axis to flip [default=False]
        crosshair: list [x, y], print crosshair at coordinates. [default=False]
        scale: int, factor to linear interpolate the input, time dimension is not interpolated. [default=2]
        cmap: str, add matplotlib cmap to image, eg: 'jet'. [default=2]
        crop: bool, crop air from image. [default=True]
        vol_wise_norm: normalize image volume-wise, only if timeseries. [default=False]
        fps: int, gif frame per second. Max 60. [default=60]
        concat_along: concatenate multiple images along a specific axis, same rule of np.concatenate. [default=1]
    return
        file path as string
    todo: add plot all 3 views in one command
    """
    # Iterates through the first axis, collapses the last if ndim ==4
    # [ax0, ax1, ax2, ax3] == [Sagittal, Coronal, Axial, time] == [X, Y, Z, T]
    if not isinstance(img, list):
        imgsl = [img]
    else:
        imgsl = img

    toconcat = []
    for img in imgsl:
        if isinstance(img, str):
            inputimg = img
            img = nib.load(img).get_fdata()
        elif isinstance(img, nib.nifti1.Nifti1Image):
            inputimg = img.get_filename()
            img = img.get_fdata()
        elif isinstance(img, np.ndarray):
            if not path:
                raise IsADirectoryError("ERROR: when using a ndarray you must specify an output filename")
            img = img

        # Crop air areas
        if crop:
            if img.ndim == 4:
                xv, yv, zv = np.nansum(img, axis=(1, 2, 3)) > 0, \
                             np.nansum(img, axis=(0, 2, 3)) > 0, \
                             np.nansum(img, axis=(0, 1, 3)) > 0
                img, img, img = img[xv, :, :, :], \
                    img[:, yv, :, :], \
                    img[:, :, zv, :]
            else:
                xv, yv, zv = np.nansum(img, axis=(1, 2)) > 0, \
                             np.nansum(img, axis=(0, 2)) > 0, \
                             np.nansum(img, axis=(0, 1)) > 0
                img, img, img = img[xv, :, :], \
                    img[:, yv, :], \
                    img[:, :, zv]

        viewsstr = {'sagittal': 0, 'coronal': 1, 'axial': 2}
        views = {0: [0, 1, 2], 1: [2, 0, 1], 2: [1, 2, 0]}  # move first the dimension to slice for chosen view
        if isinstance(view, str):
            view = viewsstr[view]
        if img.ndim == 4:
            img = np.moveaxis(img, [0, 1, 2, 3], views[view] + [3])
        else:
            img = np.moveaxis(img, [0, 1, 2], views[view])

        if rotate:
            img = np.rot90(img, k=rotate, axes=rotaxes)  # Rotate along 2nd and 3rd axis by default

        if img.ndim == 4:
            img = np.moveaxis(img, 3, 0)  # push 4th dim (time) first since imageio iterates the first
            if isinstance(slice4d, bool):  # Then slice 2nd dimension to allow 3D animation
                img = img[:, img.shape[1] // 2, :, :]
            else:
                img = img[:, slice4d, :, :]

        # Winsorize and normalize intensities for plot
        Lpcl, Hpcl = np.nanpercentile(img, winsorize[0]), np.nanpercentile(img, winsorize[1])
        img[img < Lpcl], img[img > Hpcl] = Lpcl, Hpcl
        img = img * 255.0 / np.nanmax(img)
        if vol_wise_norm:  # normalize volume-wise
            img = np.array([img[idx, ...] * 255.0 / np.nanmax(img[idx, ...]) for idx in range(img.shape[0])])

        if not isinstance(flip, bool):
            img = np.flip(img, axis=flip)  # flip a dim if needed

        if not isinstance(scale, bool):  # interpol view but no time
            img = np.array([zoom(img[idx, ...], scale, order=1) for idx in range(img.shape[0])])
        else:
            scale = 1  # no interpol

        # timebar
        if timebar:
            tres = img.shape[2] / img.shape[0]
            it = 0
            for i in range(img.shape[0]):
                it += tres
                img[i, img.shape[1] - 1, 0:int(it)] = 255  # [i,0,0] is upper left corner

        # crosshair
        if isinstance(crosshair, list):
            xmask, ymask = np.zeros_like(img, dtype=bool), np.zeros_like(img, dtype=bool)
            xmask[:, crosshair[0] * scale, :], ymask[:, :, crosshair[1] * scale] = True, True
            mask = np.logical_xor(xmask, ymask)
            img[mask] = 255

        # repeat the animation backwards
        if rewind:
            img = np.concatenate([img, np.flip(img, axis=0)], axis=0)

        # set cmap
        if isinstance(cmap, str):
            cmap = plt.get_cmap(cmap)
            # return warning 'Convert image to uint8 prior to saving' but if cast it breaks
            img = cmap(img.astype(np.uint8))
        else:
            img = img.astype(np.uint8)

        # store
        toconcat += [img]

    # set outputpath if not specified
    if not path:
        path = inputimg.replace('.nii.gz', '.gif')

    # concatenate images to plot
    img = np.concatenate(toconcat, axis=concat_along)
    # write gif
    imageio.mimwrite(path, img, fps=fps)
    return path
