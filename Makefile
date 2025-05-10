#Sets the default shell for executing commands as /bin/bash and specifies command should be executed in a Bash shell.
SHELL := /bin/bash

# Color codes for terminal output
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m
COLOR_RED=\033[1;31m

# Environment name
CONDA_ENV_NAME := infrapilot-env
PYTHON_VERSION := 3.10

# Defines the targets help, install, and run as phony targets. Phony targets are targets that are not really the name of files that are to be built. Instead, they are treated as commands.
.PHONY: help install run

#sets the default goal to help when no target is specified on the command line.
.DEFAULT_GOAL := help

#Disables echoing of commands. The commands executed by Makefile will not be printed on the console during execution.
.SILENT:

#Defines a target named help.
help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  help           	Return this message with usage instructions."
	@echo "  install        	Create a conda environment and install the dependencies."
	@echo "  run            	Run infrapilot."

#Defines a target named install. This target will create a conda environment, upgrade pip and install the dependencies.
install: create-conda-env install-dependencies farewell

#Defines a target named create-conda-env. This target will create a conda environment with Python 3.10.
create-conda-env:
	@echo -e "$(COLOR_CYAN)Creating conda environment with Python $(PYTHON_VERSION)...$(COLOR_RESET)" && \
	if command -v conda >/dev/null 2>&1; then \
		conda create -y -n $(CONDA_ENV_NAME) python=$(PYTHON_VERSION) pip && \
		echo -e "$(COLOR_GREEN)Conda environment '$(CONDA_ENV_NAME)' created successfully.$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_RED)Error: conda is not installed or not in PATH.$(COLOR_RESET)" && \
		echo -e "$(COLOR_RED)Please install Anaconda or Miniconda first.$(COLOR_RESET)" && \
		exit 1; \
	fi

#Defines a target named install-dependencies. This target will install the dependencies.
install-dependencies:
	@echo -e "$(COLOR_CYAN)Installing dependencies...$(COLOR_RESET)" && \
	conda run -n $(CONDA_ENV_NAME) pip3 install -r requirements.txt >> /dev/null && \
	echo -e "$(COLOR_GREEN)Dependencies installed successfully.$(COLOR_RESET)"

#Defines a target named farewell. This target will print a farewell message.
farewell:
	@echo -e "$(COLOR_GREEN)All done! Activate your conda environment with: conda activate $(CONDA_ENV_NAME)$(COLOR_RESET)"

#Defines a target named run. This target will run infrapilot.
run:
	@echo -e "$(COLOR_CYAN)Running infrapilot...$(COLOR_RESET)" && \
	CONDA_PREFIX=$$(conda info --base) && \
	source $$CONDA_PREFIX/etc/profile.d/conda.sh && \
	conda activate $(CONDA_ENV_NAME) && \
	python app.py
