all: build

mfiles := 0.m4 1.m4
bin    := m4
objs   := machine4.o
flags  := -O0 -g -pg -Wall -pedantic -std=c99

%.m4: %.in; ./a4 $<
%.o: %.c; cc $(flags) -c -o $@ $<
$(bin): $(objs); cc $(flags) -o $@ $^
build: $(mfiles) $(bin)
clean:; -rm $(mfiles) $(bin) $(objs)
