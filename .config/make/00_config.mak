# Makefile global config
.DEFAULT_GOAL:=help
.EXPORT_ALL_VARIABLES:
.ONESHELL:
.SILENT:
MAKEFLAGS += "-j$(NUM_CORES) -l$(NUM_CORES)"
MAKEFLAGS += --silent
SHELL:=/bin/bash
.SHELLFLAGS = -eu -o pipefail -c

# Makefile colors config
bold=$(shell tput bold)
normal=$(shell tput sgr0)
errorTitle=$(shell tput setab 1 && tput bold && echo '\n')
recommendation=$(shell tput setab 4)
underline=$(shell tput smul)
reset=$(shell tput -Txterm sgr0)
black=$(shell tput setaf 0)
red=$(shell tput setaf 1)
green=$(shell tput setaf 2)
yellow=$(shell tput setaf 3)
blue=$(shell tput setaf 4)
magenta=$(shell tput setaf 5)
cyan=$(shell tput setaf 6)
white=$(shell tput setaf 7)

define HEADER
How to use me:
 make help
 make bootstrap-dev
 make ${cyan}<target>${reset}

endef
export HEADER
