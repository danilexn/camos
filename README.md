# CaMOS

### GUI for CMOS + Calcium imaging registration
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/danilexn/CMS-TEA-DZNE/actions/workflows/python-app.yml/badge.svg)](https://github.com/danilexn/CMS-TEA-DZNE/actions)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

**CaMOS** is an interactive application for CMOS and Calcium imaging registration. It's designed for browsing, detection, and easier signal processing across large datasets.

## First Steps
### Installing _CaMOS_
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

### Running _CaMOS_
To run CaMOS as a Python module, either having installed it with pip (or not), you can execute the following command
```bash
cd CMS-TEA-DZNE # or wherever the repo directory is
python -m camos
```

If you have installed it with pip, following the instructions above, you may execute _CaMOS_ with the alias:
```bash
camos
```

### Using _CaMOS_
To get detailed instructions on how to use _CaMOS_, please visit our [Wiki](https://github.com/danilexn/CMS-TEA-DZNE/wiki) page. You will find information about the core functionality and the built-in _plugins_.

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
