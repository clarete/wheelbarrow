all: build

bin   := m3
objs  := machine3.o
flags := -O0 -g -pg -Wall -pedantic -std=c99

%.o: %.c; cc $(flags) -c -o $@ $<
$(bin): $(objs); cc $(flags) -o $@ $^
build: $(bin)
clean:; -rm $(bin) $(objs)
