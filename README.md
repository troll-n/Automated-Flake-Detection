# WORK IN PROGRESS

## System Specs

* Prior Proscan III Controller
* Prior Motorized Stage
* FLIR Blackfly 5 Color Camera
* BX-51 Microscope
* Microsoft Surface Pro running Windows 

The AFD program shouldn't run into OS compaitability issues with linux or MacOS assuming all of the packages and drivers exist in said OS. As well, the specs are not that important; one can simply replace the code in the AFD program with whatever code library you're using for your specs and it'll work fine.

## Database Information

### Chip:

PRIMARY KEY Chip_id: Int, A unique integer for identifying the chip; auto_increment
Material: Str, Name of the material of the chip (Graphene or WSe2)
Size: Int, Size of the chip, millimeters squared
Image: Str, Filepath to a decent-resolution image of the entire chip

### Flake:

FOREIGN Chip_id: Int, identifies which chip the flake is on, reference from Chip
Flake_id: Int, for identifying the flake: one ID per chip but not unqiue, so different flakes on different chips may have the same flake_id
PRIMARY KEY [Chip_id, Flake_id]: Combo that identifies the particular flake on a particular chip
Thickness: Str, The name of the layer the flake is from (TAKEN FROM FLAKE CLASS)
Size: Int, Size of the flake, micrometers squared (TAKEN FROM FLAKE CLASS)
Center_x: Int, identifies in x where to move the stage to center the flake (DERIVEN FROM FLAKE CLASS) ! FIGURE DATATYPE!
Center_y: Int, identifies in y where to move the stage to center the flake (DERIVEN FROM FLAKE CLASS) ! FIGURE DATATYPE!
Confidence: Float, confidence that the flake is correctly identified (DERIVEN FROM FLAKE CLASS)
LowMag: Str, Filepath to a 2.5x magnification image of the flake
MedMag: Str, Filepath to a 20x magnification image of the flake 
HighMag: Str, Filepath to a 50x magnification image of the flake


IMAGES NOT STORED ON DATABASE (WOULD DRASTICALLY SLOW DATABASE WRITES AND READS). Instead, images are stored natively.

File Structure:

AutoFlakeDetect
| -- Output
|
| ----Chip 1 (Image of chip_id = 1 exists here) 
| ------Flake 1 (All images of chip_id = 1, flake_id = 1 exists here)
| ------Flake 2 (etc)
| ------Flake {flake_id} (etc) 
|
| ----Chip 2 (etc)
| ------Flake {flake_id} (etc)
|
| ----Chip {chip_id} (etc)
| ------Flake {flake_id} (etc)

Chips that have been discarded can have their directory under Output as well as all of their sub-directories deleted; just keep in mind that this doesn't automatically drop them from the database.

## Installation

To install and set up your system to use the Automated Flake Detector, check out the [installation instructions](INSTALL.md).

## References

The machine learning based detection model in this system uses the detection algorithm from the paper [An open-source robust machine learning platform for real-time detection and classification of 2D material flakes](https://iopscience.iop.org/article/10.1088/2632-2153/ad2287), by authors Jan-Lucas Uslu and Taoufiq Ouaj and David Tebbe and Alexey Nekrasov and Jo Henri Bertram and Marc Schütte and Kenji Watanabe and Takashi Taniguchi and Bernd Beschoten and Lutz Waldecker and Christoph Stampfer.

## Contact

This Repo is currently maintained by [Patrick Kaczmarek](mailto:pkaczmar@andrew.cmu.edu). 
If one is interested in the GMM Detector, the [2DMatGMM Github](https://github.com/Jaluus/2DMatGMM?tab=readme-ov-file) may be of use.