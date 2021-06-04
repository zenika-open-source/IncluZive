# IncluZive
Une solution générique qui, acceptant une source de donnée, reconnaîtrait les données sensibles ou à caractère personnelle en utilisant un système intelligent, et appliquerait des techniques d'anonymisation robustes.

## Usage
### User mode
To run the main script (in order to anonymize a resume): PYTHONPATH=src python src/core/main.py <input_file_name/input_folder_name> <output_folder_name>

### Dev mode
To run tests: PYTHONPATH=src python -m pytest -p no:warnings


## Roadmap

## Prerequisites
Python 3.8.8

Jupyter Notebook 6.3.0

## Requirements
### User mode
1) Install project requirements via command: pip install -r requirements.txt
2) Install **medium** sized french corpus via: python -m spacy download fr_core_news_md

### Dev mode
Install project dev requirements via command: pip install -r requirements-dev.txt


## Licence