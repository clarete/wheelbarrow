all: bin

bin = vm
obj = main.o vm.o
vm.c main.c: vm.h
%.o: %.c; gcc -c $^ -o $@ -DTEST

$(bin): $(obj); gcc -o $@ $^
clean:; -rm $(obj) $(bin)
bin: $(bin)
