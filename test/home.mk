# makefile
# rda test suite

# make 'all' be the default target
all:

TESTS += atom-test
TESTS += xml-test

$(TESTS): ../librda.a

atom-test: atom-test.o
#xmltest: xmltest.o

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

