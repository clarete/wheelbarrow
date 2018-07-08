all: build

bin    := base64
objs   := main.o
flags  := -O0 -g -Wall -pedantic -std=c99

%.o: %.c; cc $(flags) -c -o $@ $<
$(bin): $(objs); cc $(flags) -o $@ $^
build: $(bin)
clean:; -rm $(bin) $(objs)
