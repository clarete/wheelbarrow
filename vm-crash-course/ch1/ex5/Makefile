all: build

mfiles := 0.m5 1.m5 2.m5
bin    := m5
objs   := machine5.o
flags  := -O0 -g -pg -Wall -pedantic -std=c99

%.m5: %.in; ./a5 $<
%.o: %.c; cc $(flags) -c -o $@ $<
$(bin): $(objs); cc $(flags) -o $@ $^
build: $(mfiles) $(bin)
clean:; -rm $(mfiles) $(bin) $(objs)
