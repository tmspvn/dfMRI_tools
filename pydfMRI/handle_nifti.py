import numpy as np
import nibabel as nib
import itertools as itt
import os


def save_nifti(input_img: np.ndarray, save_name: str, affine_transf: np.ndarray = np.eye(4),
               header: nib.nifti1.Nifti1Header = []) -> None:
    """
    Function that creates a Nifti1image and save it as .nii.gz
    
    Args:
        input_img (np.ndarray): array to save
        save_name (str): name to use to save
        affine_transf (np.ndarray): 4x4 array, affine transformation
        header (nib.nifti1.Nifti1Header): header of the Nifti file
    
    """
    if header:
        img = nib.Nifti1Image(input_img, affine_transf, header)
    else:
        img = nib.Nifti1Image(input_img, affine_transf)

    nib.save(img, save_name)


def load_affine(img_path: str) -> np.ndarray:
    """
    Function that returns the affine matrix from a nifti image
    
    Args:
        img_path (str): path of the nifti image
    
    Returns:
        affine matrix (np.ndarray)
        
    """

    img = nib.load(img_path)
    return img.affine


def quicknii(inimg, func, outimg="/path/newimg.nii.gz", *args, **kwargs):
    """
    "That's pure magic!" - Everyone using this function.
    Usage: power 2 of img.nii and save with newname
        quicknii('/path/to/img.nii[gz]', np.power, outimg=path/to/newimg.nii[.gz], 2)

    Args:
        inimg : <str>, path to input volume
        func : <func>, function to apply to the new image, image:np.array must be the first input of the func
        outimg : <str, False, None>, how to return the output image
                <str> -> 'full/path/where/to/save/newimg.nii' and return <outimg:str>
                <None> -> OVERWRITE computation to inimg
                <False> -> return np.array
        *args,**kwargs : additional arguments for the input function

    Return:
          see outimg parameter description

    Version 1.0.2, 18/01/22
    """
    if isinstance(inimg, nib.nifti1.Nifti1Image):
        img = inimg
    else:
        img = nib.load(inimg)

    aff, hdr = img.affine, img.header
    newimg = nib.Nifti1Image(func(img.get_fdata(), *args, **kwargs),
                             affine=aff, header=hdr)
    if outimg is None:
        nib.save(newimg, inimg)  # overwrite input img
        return inimg
    elif outimg is False:
        return newimg  # return np.array()
    else:
        if outimg is True:
            outimg = newimg.replace('.nii', '_quick.nii')
        nib.save(newimg, outimg)
        return outimg  # save new image and return path


def gzip(file, gz):
    """
    Function that zips or unzips the filename file
    Args:
        filename : str
        zip : bool, true -> zip, false -> unzip
    Return:
        new_filename : str
    """
    if gz == False:
        newname_file = file.replace('.gz', '')
        os.system(f"gzip -f -c -d {file} > {newname_file}")
    elif gz == True:
        os.system(f"gzip {file} -f")
        newname_file = f'{file}.gz'
    else:
        newname_file = None
    return newname_file


def compare_headers(*args, comp_bytes=False):
    """
    Print sequentially and compare all combinations of couples of headers, affine and header bytes
    Args:
        *args: path to files
        comp_bytes: Do header bytes comparison, default False
    """
    c = color
    for comb in itt.combinations(args, 2):
        hdr_0, aff_0, name_0 = dict(nib.load(comb[0]).header), nib.load(comb[0]).affine, os.path.basename(comb[0])
        hdr_1, aff_1, name_1 = dict(nib.load(comb[1]).header), nib.load(comb[1]).affine, os.path.basename(comb[1])
        hdr_ref = nifti_fields()
        printonce = True
        for k in hdr_0.keys():
            if np.all(str(hdr_0[k]) != str(hdr_1[k])):
                # Set spaces
                s = 20
                space0 = ((s - 5) - len(k)) * ' '
                space1 = (s - len(str(hdr_0[k]))) * ' '
                space = (s - len(str(hdr_1[k]))) * ' '
                # Print filenames once
                if printonce:
                    print('\n', (s - 5 + 2) * ' ', c.CBLUE, name_0, c.ENDC, sep='')  # s -5 + 2 since len(', ') = 2
                    print((s - 5 + 2) * ' ', '|', (s + 1) * ' ', c.CRED, name_1, c.ENDC,
                          sep='')  # 30 + 4 since len(', ') = 2 * 2 = 4
                    print((s - 5 + 2) * ' ', '\u2193', (s + 1) * ' ', '\u2193', sep='')  # 45 + 6
                    printonce = False
                # Print the comparison
                hdr_0[k] = hdr_0[k].tolist()
                hdr_1[k] = hdr_1[k].tolist()
                # Make list properly readable when printed
                if (isinstance(hdr_0[k], list) and isinstance(hdr_1[k], list)) and (
                        len(hdr_0[k]) > 2 or len(hdr_1[k]) > 2):
                    for i in range(len(hdr_0[k])):
                        space1 = (s - len(str(hdr_0[k][i]))) * ' '
                        space = (s - len(str(hdr_1[k][i]))) * ' '
                        if i == 0:  # First row
                            print(k, space0[0:-1] + '[' + str(hdr_0[k][i]),
                                  space1 + '[' + str(hdr_1[k][i]), space + hdr_ref[k], sep=', ')
                        elif i == len(hdr_0[k]) - 1:  # Last row
                            print(' ' * len(k), space0 + str(hdr_0[k][i]) + ']',
                                  space1[0:-1] + str(hdr_1[k][i]) + ']', sep=', ')
                        else:
                            print(' ' * len(k), space0 + str(hdr_0[k][i]),
                                  space1 + str(hdr_1[k][i]), sep=', ')
                else:
                    print(k, space0 + str(hdr_0[k]), space1 + str(hdr_1[k]), space + hdr_ref[k], sep=', ')

        # Affine comparison
        if np.any(aff_0 != aff_1):
            print('\nAffine:\n')
            print(c.CBLUE, name_0, c.ENDC, '\n', aff_0)
            print(c.CRED, name_1, c.ENDC, '\n', aff_1)
            print(f'{name_0} - {name_1}', '\n', aff_0 - aff_1)
        # Bytes comparison
        if comp_bytes:
            with open(comb[0], "rb") as im0, open(comb[1], "rb") as im1:
                im_0, im_1 = im0.read()[0:353], im1.read()[0:353]
                different_bytes = [i for i in range(0, 353) if im_0[i] != im_1[i]]
            print(f'\nHeader bytes differ in {len(different_bytes)}/348, index:\n {different_bytes}')
    print('https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/')


def cpheader(from_im, to_im, newimg=None, cpbytes=False):
    """
    Copy the header by replacing the header of to_im with the header of from_im.
    By default, cpheader overwrites to_im, newimg='path' to save a new img

    Args:
        from_im, to_im: path to nifti files
        newimg: filename to save new file instead of overwrite HD
        cpbytes: copy bytes instead of loading with nibabel

    """
    # ToDo: test copy bytes
    if not cpbytes:
        to_im_name = to_im
        from_im = nib.load(from_im)
        to_im = nib.load(to_im)
        new_img = to_im.__class__(to_im.dataobj[:], from_im.affine, from_im.header)
        if newimg:
            new_img.to_filename(newimg)
        else:
            out = to_im_name
            os.rename(out, out.replace('.nii', '__TMP4HDRCOPY__.nii'))
            new_img.to_filename(out)
            os.remove(out.replace('.nii', '__TMP4HDRCOPY__.nii'))
    else:
        with open(from_im, "rb") as donor:
            if newimg:
                with open(newimg, "wb") as receiver:
                    receiver.seek(0)  # set bytes offset at 0
                    receiver.write(donor.read()[0:349])  # First 348 bytes are the header
                    receiver.seek(349)  # set bytes offset at 349
                    with open(to_im, "rb") as datadonor:
                        receiver.write(datadonor.read()[349:])  # write data from the 349 byte
            else:
                with open(to_im, "wb") as receiver:
                    receiver.seek(0)  # set bytes offset at 0
                    receiver.write(donor.read()[0:349])  # First 348 bytes are the header


def nifti_fields():
    """return dict with all field description from: https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h """
    fields = {'sizeof_hdr': 'int, MUST be 348',
              'data_type': 'char, ++UNUSED++',
              'db_name': 'char, ++UNUSED++',
              'extents': 'int, ++UNUSED++',
              'session_error': 'char, ++UNUSED++',
              'regular': 'char, ++UNUSED++',
              'dim_info': 'char, MRI slice ordering',
              'dim': 'short, Data array dimensions',
              'intent_p1': 'float, 1st intent parameter',
              'intent_p2': 'float, 2nd intent parameter',
              'intent_p3': 'float, 3rd intent parameter',
              'intent_code': 'short, NIFTI_INTENT_* code',
              'datatype': 'short, Defines data type!',
              'bitpix': 'short, Number bits/voxel',
              'slice_start': 'short, First slice index',
              'pixdim': 'float, Grid spacings',
              'vox_offset': 'float, Offset into .nii file',
              'scl_slope': 'float, Data scaling: slope',
              'scl_inter': 'float, Data scaling: offset',
              'slice_end': 'short, Last slice index',
              'slice_code': 'char, Slice timing order',
              'xyzt_units': 'char, Units of pixdim[1..4]',
              'cal_max': 'float, Max display intensity',
              'cal_min': 'float, Min display intensity',
              'slice_duration': 'float, Time for 1 slice',
              'toffset': 'float, Time axis shift',
              'glmax': 'int, ++UNUSED++',
              'glmin': 'int, ++UNUSED++',
              'descrip': 'char, any text you like',
              'aux_file': 'char, auxiliary filename',
              'qform_code': 'short, code{0:arbitrary,1:scanner,2:anatomical,3:talairach,4:MNI}',
              'sform_code': 'short, code{0:arbitrary,1:scanner,2:anatomical,3:talairach,4:MNI}',
              'quatern_b': 'float, Quaternion b param',
              'quatern_c': 'float, Quaternion c param',
              'quatern_d': 'float, Quaternion d param',
              'qoffset_x': 'float, Quaternion x shift',
              'qoffset_y': 'float, Quaternion y shift',
              'qoffset_z': 'float, Quaternion z shift',
              'srow_x': 'float, 1st row affine transform',
              'srow_y': 'float, 2st row affine transform',
              'srow_z': 'float, 3st row affine transform',
              'intent_name': "char, 'name' or meaning of data",
              'magic': 'char, MUST be "ni1\\0" or "n+1\\0"'}
    return fields


class color:
    ''' color handling '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    CBLACK = '\33[30m'
    CRED = '\33[31m'
    CGREEN = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE = '\33[36m'
    CWHITE = '\33[37m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
