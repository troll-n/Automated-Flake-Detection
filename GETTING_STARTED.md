## Getting Started

This document is meant to be read after everything is already installed; check out [INSTALL.md](INSTALL.md) if this is not done.

## Training the Model using your own Data

To interactively train the model using your own data, we have provided a Jupyter Notebook `Interactive_Parameter_Estimation.ipynb` in the `GMMDetector` folder.
You can follow the instructions in the notebook to train the model using your own data. But, this repo already has a model for graphene, so if you're concerned with graphene you'll be fine with the current model.

## Using the AFD Program

Once all of your hardware is setup and conencted to this laptop, you can run the AFD detector with all of the proper arguments. Here's the format for arguments:
```shell

python path/to/autoFlakeDetector.py --material str --size int --min_confidence float --chip_x float --chip_y float

```
* **material:** The material to process, string; default is "Graphene"
* **size:** The size threshold in pixels, int; default is 200. *You should leave this argument alone unless you're debugging.*
* **min_confidence:** Any flakes that the detector picks up that has a confidence level below this will be dropped, float; default is 0.5. *min_confidence of 0 will show all flakes that the detector picks up*
* **chip_x:** Chip's size with respect to the x-axis, float; default is 10
* **chip_y:** Chip's size with respect to the y-axis, float; default is 10

Make sure that you replace path\to\AutoFlakeDetector.py with a valid path to the autoFlakeDetector. Here's an example of how to run the program from shell while already navigated to the Automated-Flake-Detection directory, with a graphene chip that's 2.5mm by 2.5mm, with a minimum confidence of 75%.
```shell

python AutoFlakeDetect/autoFlakeDetector.py --min_confidence 0.75 --chip_x 2.5 --chip_y 2.5

```
Note that all arguments are optional; if you wanted to put in a chip of graphene that just so happens to be 10mm by 10mm and wanted all flakes with a confidence statistic greater than 50%, you could just call the program with no arguments.

One should also take care ensure that the microscope is currently aimed at the top left corner of the chip. We plan on adding computer vision capabilities to the program such that it can autodetect where the chip is on the stage, but for now it's more about making sure the program can accurately and quickly find a flake. Thus, give us (the gremlins in the computer runnning the code for you) a hand by aligning the chip properly.


## Getting Results

Currently, the only way to get results from the program is to ask for it manually using queries to the AFD_db database. We plan on making the UI interface more friendly by introducing a python notebook to do it all for you, but for now that's it.