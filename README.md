![Darknet Logo](http://pjreddie.com/media/files/darknet-black-small.png)

# Darknet #
Darknet is an open source neural network framework written in C and CUDA. It supports CPU and GPU computation.

For more information see the [Darknet project website](http://pjreddie.com/darknet).

For questions or issues please use the [Google Group](https://groups.google.com/forum/#!forum/darknet).

## Installation

For general information on installation, you can take a look at [darknet's website](https://pjreddie.com/darknet/install/).

To install on MacOsx :
```
cd darknet
make
```

To install on Windows :

Follow this issue : https://github.com/pjreddie/darknet/issues/721

## Run

To execute the prediction's command, you will need to download: 
- *extraction.weights* [here](http://pjreddie.com/media/files/extraction.weights) (80MB)
- *yolo.weights* [here](http://pjreddie.com/media/files/yolo.weights) (1GB)
- *yolo.cfg* [here](https://raw.githubusercontent.com/cvjena/darknet/master/cfg/yolo.cfg) (3KB)
- *yolov3.weights* [here](https://pjreddie.com/media/files/yolov3.weights) (237MB)

## Usage

First, create a `./data` directory and store all your pictures into it. In that directory, create a subdirectory for every picture: for a picture named `"voitures.png"`, you will store this file in a subdirectory named `voitures`. The path to the screenshot will be `./data/voitures/voitures.png`.

### Automatic labelization

To launch YOLO and store the coordinates of the items recognized:
* for windows
```bash
python python/rec_fct_slid_win.py mac data/voitures/ voitures
```
* for mac
```bash
python python/rec_fct_slid_win.py win data/voitures/ voitures
```

### Visualize recognized areas

To check if the items automatically recognized are correct and visualize them, run `drawing_rect.py` as follows:
```bash
python python/drawing_rect.py --image data/voitures/voitures.png
```

### Manual labelization

To labellize manually your pictures or screenshots, run `click_and_get_coord.py` as follows:
```bash
python python/click_and_get_coord.py data/voitures/voitures voitures
```
