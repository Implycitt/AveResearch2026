## Code

---

All relevant code used in this research and for the purpose of this research is contained within this directory.

## Prerequisites

---

1. Ensure that the latest version of python is installed.

```bash
# if on windows
python --version

# if on macOS/linux
python3 --version
```

2. Ensure that pip is also installed.

```bash
# if on windows
pip --version

# if on macOS/linux
pip3 --version
```

3. Ensure git is installed.

```bash
git --version
```

## Installation

--- 

All data and code are contained within this repository meaning that anyone can run the experiments locally and grab the ouputs.

1. Clone the repository

```bash
git clone https://github.com/Implycitt/AveResearch2026.git

cd AveResearch2026
```

2. Create and source the python virtual environment

```bash
# if on windows
python -m venv .venv
.\.venv\Scripts\activate

# if on macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

```

3. Install the packages from the requirements.txt file

```bash
pip install -r requirements.txt
```

## Subdirectories

---

The code is split into the subdirectories, Acquisition and Data based on its function. The documentation is within each corresponding subdirectory in the README.md file.

* [Acquisition](https://github.com/Implycitt/AveResearch2026/blob/main/src/Acquisition/README.md) readme for the code documenting how I got 600.000+ observations.
* [Data](https://github.com/Implycitt/AveResearch2026/blob/main/src/Data/README.md) readme for the code used to analyze the observations.