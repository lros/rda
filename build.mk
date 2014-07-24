# Include this makefile as follows:
#   RDA_TOP =? $(shell rdainfo.py --top)
#   include $(RDA_TOP)/build.mk

# First make sure 'all' is the default target.
all:

# In case the caller didn't do it:
RDA_TOP ?= $(dir $(filter build.mk,$(MAKEFILE_LIST)))
# If that didn't work, do it the more expensive way.
RDA_TOP ?= $(shell rdainfo.py --top --unknown)
ifeq ($(RDA_TOP),unknown)
    $(error Not in an RDA sandbox)
endif

include $(RDA_TOP)/build/project.mk

_HOST ?= $(shell rdainfo.py --host --unknown)
ifeq ($(_HOST),unknown)
    $(error Cannot determine host type)
endif

include $(RDA_TOP)/build/host_$(_HOST).mk

ifndef TARGET
    ifeq ($(words $(_TARGETS)),1)
        TARGET:=$(_TARGETS)
    endif
endif

ifndef CONFIG
    ifeq ($(words $(_CONFIGS)),1)
        CONFIG:=$(_CONFIGS)
    endif
endif

ifdef RDA_ALLOW_TARGET_CONFIG_GOAL
    ifeq ($(words $(MAKECMDGOALS)),1)
        _tail = $(wordlist 2,$(words $(1)),$(1))
        _RECURGOALS := $(subst -, ,$(MAKECMDGOALS))
        ifndef TARGET
            # Take first part of goal for the TARGET.
            TARGET := $(firstword $(_RECURGOALS))
            _RECURGOALS := $(call _tail,$(_RECURGOALS))
            _DORECUR := 1
        endif
        ifndef CONFIG
            # Take first remaining part of goal for the CONFIG.
            CONFIG := $(firstword $(_RECURGOALS))
            _RECURGOALS := $(call _tail,$(_RECURGOALS))
            _DORECUR := 1
        endif
    endif
endif

ifdef _DORECUR

.PHONY: $(MAKECMDGOALS)
$(MAKECMDGOALS):
	$(MAKE) -f $(firstword $(MAKEFILE_LIST)) TARGET=$(TARGET) \
	    CONFIG=$(CONFIG) $(_RECURGOALS)

else

    include $(RDA_TOP)/build/main.mk

endif

