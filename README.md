# Testbed for Conflict Resolution Policies in Autonomous Vehicles

## Prerequisites

Before running the testbed, you need to download and install Eclipse SUMO. The latest version can be found here: https://www.eclipse.org/sumo/

You will also need to install any Python modules required, which can be done by running the following command from the repo folder in a terminal:

```pip install -r requirements.txt```

You will need a ```config.yaml``` file to define user settings. A template, ```config.yaml.template``` is available.

## Running the program

To startup the testbed, open a terminal and navigate to the folder where the testbed is located. Then, enter the following command:

```python main.py```

There are also several optional commands:

- ```--no_gui``` allows you to run simulations without displaying the SUMO GUI.
- ```--no_log``` allows you to disable data logs.
- ```--number=<num>``` or ```-n=<number>``` instructs the testbed to run a specific number of simulations
    - (e.g. ```python main.py -n=10``` will cause the testbed to run 10 simulations)
- ```--output_folder_name=<name>``` or ```-o=<name>``` allows you to specify the folder name where data is logged to
    - (e.g. ```python main.py -o=priority``` causes the simulation to store outputs in a log folder named "priority")

## Quick summary of features

### User settings

User settings can be defined in the ```config.yaml``` file. This can be used to define properties of the road network, agents in the simulation, etc.
An example is given in the form of ```config.yaml.template```.

### Data logs

Data logs from simulations are stored in the ```logs``` folder. Each subfolder comes from a separate execution of the program.
