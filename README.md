# BiofeedbackAssistedMusic
The goal of this project is to boost exercise performance by using biofeedback-assisted music.    
## Instructions
### Install for Dev
In order to set up for development, from project root run 
```bash
bash dev_setup.sh
```
This will setup a virtual env and install the biofeedback module in [editable install mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) with all dependencies specified in `pyproject.toml`
### Install for use
make sure you have the `venv` module installed.
#### Create virtual env
```bash
python -m venv env
source env/bin/activate
```
#### Install biofeedback from source
```bash
pip install git+ssh://git@github.com/ItaiAllouche/BiofeedbackAssistedMusic.git
```
