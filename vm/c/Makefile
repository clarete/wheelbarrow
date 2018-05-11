all: bin

bin = vm
obj = main.o vm.o bits.o
vm.c main.c: vm.h
%.o: %.c; gcc -Wall -g -O0 -c $^ -o $@ -DTEST

$(bin): $(obj); gcc -g -O0 -o $@ $^
clean:; -rm $(obj) $(bin)
bin: $(bin)
