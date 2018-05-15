all: bin

bin = prefix2postfix
obj = main.o
flags = -Wall -g -O0
%.o: %.c; gcc $(flags) -o $@ -c $^
$(bin): $(obj); gcc $(flags) -o $@ $^
clean:; -rm $(obj) $(bin)
bin: $(bin)
