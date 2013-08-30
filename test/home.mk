# makefile
# rda test suite

# make 'all' be the default target
all:

TESTS += atom-test

$(TESTS): ../librda.a

#t1_init: t1_init.cpp ../libVgoFramework.a
#t2_props: t2_props.cpp ../libVgoFramework.a
#t3_connections: t3_connections.cpp ../libVgoFramework.a

atom-test: atom-test.o

# Location of rda include files
CPPFLAGS += -I..
CPPFLAGS += -DBOOST_TEST_DYN_LINK
#CPPFLAGS += -O3
CPPFLAGS += -g

# Location of Vgo Framework library
LDFLAGS += -L..
#LDFLAGS += -L/usr/local/lib

LDLIBS += -lrda
LDLIBS += -lboost_unit_test_framework
#LDLIBS += -llacewing
#LDLIBS += -lstdc++

.PHONY: all lib clean

all: lib $(TESTS)

lib:
	make -C .. -f home.mk

clean:
	make -C .. -f home.mk clean
	rm -f *.o $(TESTS)

