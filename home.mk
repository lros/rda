all: librda.a

#CPPFLAGS += -g
#CPPFLAGS += -I/usr/local/include

#LDLIBS += -llacewing
#LDFLAGS += -L/usr/local/lib

atom.o: atom.hpp
rdaxml.o: rdaxml.hpp

librda.a: atom.o rdaxml.o
	ar rs $@ $^

clean:
	rm *.o librda.a
