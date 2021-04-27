.PHONY: clean dirs

#################################################################################
# GLOBALS                                                                       #
#################################################################################

TEMP_DIR ?= /tmp
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON_INTERPRETER = python3.8
IF_VENV=$(shell $(PYTHON_INTERPRETER) -c 'import sys; print ("TRUE" if hasattr(sys, "real_prefix") else "FALSE")')

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Check if an virtual environment is activated
check-venv:
ifeq ($(IF_VENV),FALSE)
	$(error No virtualenv activated)
endif
	@true

## Create directories that are ignored by git but required for the project
dirs:
	mkdir -p build/reports

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/*

## Generate classification report
report: dirs
	papermill Notebooks/EvaluationMetrics/Evaluation\ metrics.ipynb ./build/reports/classification.ipynb \
              -p path Notebooks/EvaluationMetrics -p reports_path ./reports

## Start JupyterLab in background
start-jupyterlab: check-venv
	nohup jupyter lab > $(TEMP_DIR)/jupyterlab.log 2>&1 & echo $! > $(TEMP_DIR)/jupyterlab.pid &

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { h;s/.*//;:doc" -e "H;n;s/^## //;t doc" -e "s/:.*//;G;s/\\n## /---/;s/\\n/ /g;p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
	        -v ncol=$$(tput cols) \
	        -v indent=19 \
	        -v col_on="$$(tput setaf 6)" \
	        -v col_off="$$(tput sgr0)" \
	'{ \
	        printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
	        n = split($$2, words, " "); \
	        line_length = ncol - indent; \
	        for (i = 1; i <= n; i++) { \
	                line_length -= length(words[i]) + 1; \
	                if (line_length <= 0) { \
	                        line_length = ncol - indent - length(words[i]) - 1; \
	                        printf "\n%*s ", -indent, " "; \
	                } \
	                printf "%s ", words[i]; \
	        } \
	        printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
