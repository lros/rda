# project.mk
# Project-specific but platform- and host-independent - RDA build system

# TODO this file could be incorporated into build.mk

# List the legal configurations
_CONFIGS := release debug

# Parent directory where libraries are placed (and searched for)
# during the build.
_LIBDIR := $(RDA_TOP)/lib

# Uncomment to allow "make TARGET CONFIG ..." style invocation.
# (Or set in your environment.)
# RDA_ALLOW_TARGET_CONFIG_GOAL := 1

