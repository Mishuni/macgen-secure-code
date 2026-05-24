SRCS := $(wildcard *.cpp)
OBJS := $(SRCS:.cpp=.o)

all: $(OBJS)

%.o: %.cpp
	g++ -c $< -o $@
