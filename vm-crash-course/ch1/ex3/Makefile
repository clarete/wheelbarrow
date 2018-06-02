all: build

mfiles := 0.m3 1.m3 2.m3
bin    := m3
objs   := machine3.o
flags  := -O0 -g -pg -Wall -pedantic -std=c99

%.m3: %.in; ./a3 $<
%.o: %.c; cc $(flags) -c -o $@ $<
$(bin): $(objs); cc $(flags) -o $@ $^
build: $(mfiles) $(bin)
clean:; -rm $(mfiles) $(bin) $(objs)
