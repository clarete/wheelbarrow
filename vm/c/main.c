#include "vm.h"

extern void test_stack0 (void);
extern void test_bytecode0 (void);

int main () {
  test_stack0 ();
  test_bytecode0 ();
}
