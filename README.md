# CaMOS

### GUI for CMOS + Calcium imaging registration
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/danilexn/CMS-TEA-DZNE/actions/workflows/python-app.yml/badge.svg)](https://github.com/danilexn/CMS-TEA-DZNE/actions)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

**CaMOS** is an interactive application for CMOS and Calcium imaging registration. It's designed for browsing, detection, and easier signal processing across large datasets.

## Installation
CaMOS can be installed on most macOS, Linux, and Windows systems with Python >=3.7. Currently, you can just install CaMOS from source. We are planning on adding pip in the future.

```bash
# Clone the repository locally
git clone https://github.com/danilexn/CMS-TEA-DZNE.git
# Navigate to the directory
cd CMS-TEA-DZNE
# Install using pip (make sure that pip is alias to pip for python >=3.7
pip install -e '.[all]'
```

Make sure you have an internet connection during the installation process, as pip will require it to automatically install all dependencies. Otherwise, dependencies listed under `requirements.txt` are expected to be installed beforehand.

## Running _CaMOS_
To run CaMOS as a Python module, either having installed it with pip (or not), you can execute the following command
```bash
cd CMS-TEA-DZNE # or wherever the repo directory is
python -m camos
```

If you have installed it with pip, following the instructions above, you may execute _CaMOS_ with the alias:
```bash
camos
```

## Creating plugins
**CaMOS** offers a modular way to create plugins, which are automatically loaded when you run the program. This is based in the concept of *Tasks*. There are three types of *Tasks*, which inherit from a universal *Base* task. *Base* contains the essential methods to run, plot and move the data through CaMOS - and generate the corresponding GUI signals. To write a plugin, you first have to select between one of the four *Tasks* available:

1. Opening: will provide a File Dialog, with (possibly) a filter for specific extension(s); then, it will provide a custom GUI (if required) automatically created for the `_run()` method. You can choose to store the input data in both the Image or Signal model (depending on the data input). You can also use any of the default data reading methods (e.g., multi-page TIFF and other common image formats are available by default), or develop your own file parsing methods.
2. Saving: analogous to Opening, but for saving files. It will provide a common framework to retrieve data from the Image or Signal models.
3. Analysis: takes either Image or Signal data, and will produce new data to be stored in the Signal model. This should be used to develop plugins that analyze datasets; e.g., calculate Mean Firing Rate from event tracks.
4. Processing: similar to Analysis, but outputs to the Image model, by default. This should be used when developing plugins for image processing; e.g., segmentation, registration.

Regardless of the type of *Task*, the basic structure of a plugin must be as follows (will use https://github.com/danilexn/CMS-TEA-DZNE/blob/main/camos/plugins/meanfiringrate/meanfiringrate.py as an example):

#### 0. Create the plugin folder and file
You must create a directory with a unique name for your plugin, e.g., org.camos.meanfiringrate. Then, inside that directory, you may create a .py file, with the same name. This will be used as the entry point of the plugin, in case there are more files that implement extra functionality. Additionally, you must create a file, in that same directory, called `__init__.py`, containing the following (for a plugin where the entrypoint is `meanfiringrate.py`):
```python
__all__ = ["meanfiringrate"]
```

#### 1. Imports that will be used by the plugin
You can import any modules that may be useful for your plugin, e.g., `numpy` (careful, the user may have not installed them beforehand!)
```python
import numpy as np
```

More importantly, you have to import the class of the type of *Task* that will be used as the base for your plugin. In this example, *Analysis* was chosen.
```python
from camos.tasks.analysis import Analysis
```

Then, the types of input that the plugin will use as its main entry point, e.g., numeric parameters, or list of opened images:
```python
from camos.utils.generategui import (
    DatasetInput,
    NumericInput,
    ImageInput,
    CustomComboInput,
)
from camos.utils.units import length
```

Lastly, you can import any additional utilities from CaMOS, i.e., the length dictionary to translate between descriptive names and abbreviations for common metric units:

```python
from camos.utils.units import length
```

#### 2. The plugin class
At this point, you have to create a class that will contain all the methods of your plugin. There, you have to specify the name that will be displayed in the GUI, and the required input data (either image - from Image model-  or dataset - from Signal model -); this way, if no data is available in the models, the plugin will throw an error. Also, you must inherit the class for the specific *Task* you chose.

```python
class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"
    required = ["image", "dataset"]
```

#### 3. The initialization method
By default, the `__init__` method can be ommited. Otherwise, you can configure any additional extensions to the base variables that are provided by the classes *Analysis*, and its parent *Base*. For example, to ensure that finishing the main task of the plugin will store the `self.output` as a new data object in the Signal model:

```python
def __init__(self, *args, **kwargs):
        super(MeanFiringRate, self).__init__(*args, **kwargs)
        self.finished.connect(self.output_to_signalmodel)
```

#### 4. The `_run()` method
Inside this, you can write all the code that will be executed as the main "entry" point of the plugin; think of this as the `main()` function. Importantly, the arguments of this method must be annotated with the type of input in order to generate a GUI for these:
```python
def _run(
        self,
        duration: NumericInput("Total Duration (s)", 100),
        scale: NumericInput("Axis scale", 1),
        _i_units: CustomComboInput(list(length.keys()), "Axis units", 0),
        _i_data: DatasetInput("Source Dataset", 0),
        _i_mask: ImageInput("Mask image", 0),
    )
```

Once the arguments have been specified, you can write the body of the function. Take into account that the *Base* class provides access to the Image model through the `self.model` object, and to the Signal model through the `self.signal` object. Also, the output data should be stored as a `self.output` object, so the default *finished* signal will move whatever is in this object to the Signal data model.

#### 5. The `_plot()` method
You can write here any plotting scheme for the underlying pyplot engine. You can access the figure in the viewport with `self.plot.fig`, and the default axes with `self.plot.axes`. For example, in the case of the MFR plugin:

```python
def _plot(self):
        # ... code ommited
        im = self.plot.axes.imshow(
            MFR_mask / self.duration, cmap="inferno", origin="upper"
        )
        self.plot.fig.colorbar(
            im, ax=self.plot.axes, label="Mean Firing Rate (Events/s)"
        )
        self.plot.axes.set_ylabel("Y coordinate ({})".format(self.units))
        self.plot.axes.set_xlabel("X coordinate ({})".format(self.units))
```

#### 5. Finish!
The code above is enough to get your first CaMOS plugin. Just copy the directory you created in step #0 inside the camos/plugins directory, and restart the application. Your plugin should be accessible through the top menubar, inside the specific menu for the type of *Task*.

## Roadmap
See the [open issues](https://github.com/danilexn/CMS-TEA-DZNE/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**. Follow the *recipe* below to contribute to this repository:



1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License
Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact
Daniel León Periñán - [@danilexn](https://github.com/danilexn) - daniel.leon-perinan@mailbox.tu-dresden.de
Josua Seidel - [@jseidel5](https://github.com/jseidel5) - josua.seidel@mailbox.tu-dresden.de
Hani Al Hawasli - [@HaniAlHawasli](https://github.com/HaniAlHawasli) - hani.al-hawasli@mailbox.tu-dresden.de
