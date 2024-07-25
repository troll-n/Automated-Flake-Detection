# Part 1: Installation of the 2DMatGMM Package

To install and use the 2DMatGMM package, you first need to install the required dependencies. This installation process has been tested using Python 3.10.

## Setting Up a Python Virtual Environment

For optimal compatibility, we recommend setting up a new Python virtual environment and installing the required packages within that environment. If you're using `conda` as your package manager, you can create and activate the virtual environment using the following commands:

```shell
conda create --name 2DMatGMM python=3.10
conda activate 2DMatGMM
```

## Installing Required Packages

Download the Repository and navigate to the repository directory and execute the following command:

```shell
pip install -e .
```

This will install all necessary packages and makes it possible to import the package with

```python
import GMMDetector
```


## Example Setup Using Conda

Here's an example of how to install the required packages using `conda` and set up a virtual environment for 2DMatGMM:

```shell
# setup virtual environment and install required packages
conda create --name 2DMatGMM python=3.10 -y
conda activate 2DMatGMM

# clone the repository and navigate to it
git clone https://github.com/Jaluus/2DMatGMM.git
cd 2DMatGMM

# install the package as GMMdetector
pip install -e .
```
# Part 2: Hardware-related Installs

## Prior ProScan III

We already have the PriorSDK module implemented in this codebase, but one still needs to install the Prior driver. Luckily, Prior's software isn't all that bad and takes about 2 minutes to install. This install has been tested on a 64 bit Windows computer.

Go to [Prior Scientific's Software Downloads](https://www.prior.com/download-category/software) and specifically download their [ProScan III Firmware](https://www.prior.com/wp-content/themes/prior-scientific/download.php?file=512) install wizard. Once again, you don't need the SDK since it's already included in this repo for convinence. Then, follow the simple installation wizard. The AFD program will take care of finding the firmware for you, so this is all you need.

## Camera

We're using a Blackfly FLIR with the RotPy package. Run the following in your shell
```shell
python -m pip install rotpy
```
while in your venv from before. You may need to install the C++ redistributable from Microsoft if it doesn't work; see [RotPy's documentation](https://matham.github.io/rotpy/README.html). RotPy is really just another SDK.

# Part 3: MySQL Database

MySQL is the database of choice for this project. Head on over to [MySQL's community downloads](https://dev.mysql.com/downloads/installer/) and install MySQL with all reccomended packages. You're also going to want to grab the connector package by running this in your shell:

```shell
pip install mysql-connector-python
```

Once done, head on over to the [database setup python notebook](./DBSETUP.ipynb) to setup the database properly; it should only take a minute.

# Done!

This completes the setup process. Now, you're ready to use the AFD!
Check out the [Getting Started Guide](./GETTING_STARTED.md)!
