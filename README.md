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
MIT License

Copyright (c) 2021 Zenika Open Source

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.