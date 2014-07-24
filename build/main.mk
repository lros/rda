
ifeq ($(TARGET),)
    ifeq ($(words $(_TARGETS)),1)
        TARGET:=$(_TARGETS)
    else
        $(error TARGET not specified: one of $(_TARGETS))
    endif
else
    ifeq ($(filter $(TARGET), $(_TARGETS)),)
        $(error TARGET ($(TARGET)) must be one of $(_TARGETS))
    endif
endif

include $(RDA_TOP)/build/target_$(TARGET).mk

ifeq ($(CONFIG),)
    ifeq ($(words $(_CONFIGS)),1)
        CONFIG:=$(_CONFIGS)
    else
        $(error CONFIG not specified: one of $(_CONFIGS))
    endif
else
    ifeq ($(filter $(CONFIG), $(_CONFIGS)),)
        $(error CONFIG ($(CONFIG)) must be one of $(_CONFIGS))
    endif
endif

include $(RDA_TOP)/build/config_$(CONFIG).mk

MODULE ?= $(notdir $(CURDIR))

# The directory for intermediate files.
_OBJDIR := obj-$(TARGET)-$(CONFIG)

_STATIC_LIB_NAME_OF ?= lib$(1).a
RDA_LIB_STATIC := $(_OBJDIR)/$(call _STATIC_LIB_NAME_OF,$(MODULE))

_DYNAMIC_LIB_NAME_OF ?= lib$(1).so
RDA_LIB_DYNAMIC := $(_OBJDIR)/$(call _DYNAMIC_LIB_NAME_OF,$(MODULE))

RDA_EXEC ?= $(_OBJDIR)/$(MODULE)

# Process some additions to the flags governing compilation.
DEFINES += RDA_TARGET=$(TARGET)
DEFINES += RDA_CONFIG=$(CONFIG)
DEFINES += RDA_MODULE=$(MODULE)
CPPFLAGS += $(addprefix -I,$(INCLUDES))
CPPFLAGS += $(addprefix -D,$(DEFINES))

# List of all the .o files
_OBJECTS := $(addprefix $(_OBJDIR)/,$(notdir $(basename $(SOURCES))))

# Modify Make's built-in pattern rules to use _OBJDIR.
.SUFFIXES:
# Compile C
$(_OBJDIR)/%.o: %.c $(_OBJDIR)/.witness
	$(COMPILE.c) $(OUTPUT_OPTION) $<
# Compile C++
$(_OBJDIR)/%.o: %.cc $(_OBJDIR)/.witness
	$(COMPILE.cc) $(OUTPUT_OPTION) $<
# Compile C++
$(_OBJDIR)/%.o: %.cpp $(_OBJDIR)/.witness
	$(COMPILE.cpp) $(OUTPUT_OPTION) $<
# Compile Objective-C
$(_OBJDIR)/%.o: %.m $(_OBJDIR)/.witness
	$(COMPILE.m) $(OUTPUT_OPTION) $<
# Compile Objective-C++
$(_OBJDIR)/%.o: %.mm $(_OBJDIR)/.witness
	$(COMPILE.mm) $(OUTPUT_OPTION) $<

# Link an executable
$(RDA_EXEC): $(_OBJECTS)

# Link a static library
$(RDA_LIB_STATIC): $(_OBJECTS)

# Link a dynamic library
$(RDA_LIB_DYNAMIC): $(_OBJECTS)

$(_OBJDIR)/.witness:
	@mkdir -p $(_OBJDIR) && touch $@

all:
	@echo RDA_TOP is $(RDA_TOP)
	@echo _HOST is $(_HOST)
	@echo TARGET is $(TARGET)
	@echo CONFIG is $(CONFIG)
	@echo MODULE is $(MODULE)

