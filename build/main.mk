
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

# Subdirectory where libraries are placed during build.
# Executables are put there, too.
_LIBSUBDIR := $(_LIBDIR)/$(TARGET)-$(CONFIG)

_STATIC_LIB_NAME_OF ?= lib$(1).a
RDA_LIB_STATIC := $(_LIBSUBDIR)/$(call _STATIC_LIB_NAME_OF,$(MODULE))

_DYNAMIC_LIB_NAME_OF ?= lib$(1).so
RDA_LIB_DYNAMIC := $(_LIBSUBDIR)/$(call _DYNAMIC_LIB_NAME_OF,$(MODULE))

RDA_EXEC ?= $(_LIBSUBDIR)/$(MODULE)

# Process some additions to the flags governing compilation.
DEFINES += RDA_TARGET_$(TARGET)
DEFINES += RDA_CONFIG_$(CONFIG)
DEFINES += RDA_MODULE=\"$(MODULE)\"
CPPFLAGS += $(addprefix -I,$(INCLUDES))
CPPFLAGS += $(addprefix -D,$(DEFINES))
LDFLAGS += -L$(_LIBSUBDIR)

# List of all the .o files
_OBJECTS = $(patsubst %,$(_OBJDIR)/%.o,$(notdir $(basename $(SOURCES))))

# List of .d (dependency) files
_DFILES = $(_OBJECTS:.o=.d)

# Tell gcc to generate .d files while compiling
CPPFLAGS += -MD

# Never try to remake a .d file
$(_DFILES):

# Include the .d files but don't complain if any are missing
-include $(_DFILES)

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
	$(LINK.cc) $^ $(LDLIBS) -o $@

# Effectively replace Make's built-in archaic default of 'rv'.
ifeq ($(origin ARFLAGS),default)
ARFLAGS = rs
endif

# Mostly patterned after Make's built-ins.
ifndef STATICLIB.recipe
STATICLIB.recipe = $(AR) $(ARFLAGS) $@ $^
endif

# Link a static library
$(RDA_LIB_STATIC): $(_OBJECTS)
	$(STATICLIB.recipe)

# Mostly patterned after Make's built-ins.
ifndef DYNAMICLIB.recipe
DYNAMICLIB.recipe = $(LD) -shared $(LDFLAGS) $(LDLIBS) -o $@ $^
endif

# Link a dynamic library
$(RDA_LIB_DYNAMIC): $(_OBJECTS)
	$(DYNAMICLIB.recipe)

$(_OBJDIR)/.witness:
	mkdir -p $(_OBJDIR) && touch $@

$(_LIBSUBDIR)/.witness:
	mkdir -p $(_LIBSUBDIR) && touch $@

all: $(_LIBSUBDIR)/.witness

clean:
	$(RM) -r $(_OBJDIR)
	$(RM) $(RDA_LIB_STATIC) $(RDA_LIB_DYNAMIC) $(RDA_EXEC)

print:
	@echo RDA_TOP is $(RDA_TOP)
	@echo _HOST is $(_HOST)
	@echo TARGET is $(TARGET)
	@echo CONFIG is $(CONFIG)
	@echo MODULE is $(MODULE)
	@echo _OBJECTS is $(_OBJECTS)

