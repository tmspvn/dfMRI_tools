# dfMRI_tools

Python package for diffusion function magnetic resonance imaging (dfMRI) images handling.

## Description

Package that allows standard manipulation of dfMRI nifti images as well as plotting.

## Getting Started

### Dependencies

* matplotlib 3.5.3
* numpy 1.23.4
* nibabel 4.0.2
* python >= 3.10
* scipy 1.9.3

### Installing

```
conda activate your_conda_env
git clone https://github.com/ideriedm/dfMRI_tools.git
cd dfMRI_tools
pip install -e .
```
or

```
conda activate your_conda_env
pip install git+https://github.com/ideriedm/dfMRI_tools.git
```

### Updating package after local change

```
conda activate your_conda_env
cd dfMRI_tools
pip install -e .
```

### Run the doc

```
cd dfMRI_tools/docs
sphinx-apidoc -f -o ../docs/ ../pydfMRI/
make html
```

## Authors

[@ideriedm](Ines.De-Riedmatten@chuv.ch)

## Version History

* 0.0.1 (Initial Release)

## License

This project is licensed under the MIT-License - see the LICENSE.md file for details

