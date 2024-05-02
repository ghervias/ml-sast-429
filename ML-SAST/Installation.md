# Installation

## Hardware requirements:

- 8 GB of RAM to execute the prototype with the provided example
- 20 GB of available hard-disk space, if you want to run the oracle tests

## Software requirements:

- *nix operating system
- git
- python3
- pip
- docker

## Download

Obtain the source code for the ml-sast prototype by cloning this repository to a directory on your local computer.

## Alternative Download Steps
If you cannot clone the repository, you should be able to download a zip file containing the ml-sast prototype. Extract this to a location on your local computer.

## Configure Docker
As the prototype uses Docker to executes some steps of its pipeline, your user should be part of the docker group. To add your user to the docker group consult the following [link](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

## Install

As the ml-sast prototype has a variety of dependencies, it is always a good idea to create a virtual environment:

```shell
python3 -m venv /path/to/new/virtual/environment
```

Next the virtual environment needs to be activated:

```shell
source /path/to/new/virtual/environment/bin/activate
```

Afterwards the dependencies for the ml-sast prototype can be installed:

```shell
pip install -r requirements.txt
```

Finally, the ml-sast prototype can be installed:
```shell
pip install .
```

Similarly install the frontend:
```shell
cd frontend
pip install .
```

## Run ml-sast prototype

To run the ml-sast prototype have a look at the instructions in the [Usage guide](Usage.md).
