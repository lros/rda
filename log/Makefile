all: release debug

CPPFLAGS += -DRDA_MODULE=\"testModule\"
LDLIBS += -lboost_thread

release: CPPFLAGS += -DRELEASE_BUILD
release: main
#	@echo $(CPPFLAGS)

debug: CPPFLAGS += -DDEBUG_BUILD
debug: maindebug
#	@echo $(CPPFLAGS)

main: main.o log.o
	$(LINK.cc) $^ $(LDLIBS) -o $@

maindebug.o: main.cpp log.hpp
	$(COMPILE.cc) $< -o $@

maindebug: maindebug.o log.hpp log.o
	$(LINK.cc) $^ $(LDLIBS) -o $@

log.o: log.hpp

clean:
	rm -f main main.o maindebug maindebug.o log.o

