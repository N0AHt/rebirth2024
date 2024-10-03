# Repo for analysing hydra reaggregation data.

Cell tracking, calcium signal processing, and analysis of regeneration of
ensembles.


## Installation

To install this into a new mamba env:

First clone the github repo and navigate into it 
```
$ cd <directory_when_repo_will_be_cloned> # i.e. desktop or github, wherever you want the code to be
$ git clone <repo_url> # clone repo
$ cd <repo>
```

Create a new mamba environment and install python
```
$ mamba create -n rebirth python, ipykernel # env will be called rebirth. Add ipykernel if using jupyter notebooks
$ mamba activate rebirth
```

Install the package and requirements
```
$ pip install -e . # Install in editable mode for now
$ pip install -r requirements.txt
```


## Usage

- Notebooks for loading multiple tiff stacks and creating a memmap file from them
- Notebooks for loading these memmap files and visualising the data
- Notebooks for tracking the tdTomato labelled cells
- Notebooks for using the trakced tdTomato