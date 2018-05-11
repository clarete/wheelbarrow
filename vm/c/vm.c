#include <string.h>
#include "vm.h"

/* Forward declaration for instructions */

/* Integer */
static inline void vmi_iadd (vm_t *vm);
static inline void vmi_isub (vm_t *vm);
static inline void vmi_imul (vm_t *vm);
static inline void vmi_idiv (vm_t *vm);
/* Float */
static inline void vmi_fadd (vm_t *vm);
static inline void vmi_fsub (vm_t *vm);
static inline void vmi_fmul (vm_t *vm);
static inline void vmi_fdiv (vm_t *vm);
/* Symbols */
static inline void vmi_istore (vm_t *vm);
static inline void vmi_fstore (vm_t *vm);
static inline void vmi_iload (vm_t *vm);
static inline void vmi_fload (vm_t *vm);
/* Jumps */
static inline void vmi_jz (vm_t *vm);
static inline void vmi_jmp (vm_t *vm);
static inline void vmi_jmpb (vm_t *vm);
/* Callables */
static inline void vmi_call (vm_t *vm);
/* Return */
static inline void vmi_ret (vm_t *vm);


void vm_init (vm_t *vm)
{
  vm->stack_pointer = 0;
  memset (vm->stack, 0, STACK_SIZE);
}

void vm_push (vm_t *vm, void *i)
{
  vm->stack[vm->stack_pointer++] = i;
}

void *vm_pop (vm_t *vm)
{
  return vm->stack[--vm->stack_pointer];
}

static void vmi_iadd (vm_t *vm)
{
  int32_t a, b, c;
  b = *((int32_t *) vm_pop (vm));
  a = *((int32_t *) vm_pop (vm));

  c = a + b;

  vm_push (vm, &c);
}

static void vmi_isub (vm_t *vm)
{
  int32_t a, b, c;
  b = *((int32_t *) vm_pop (vm));
  a = *((int32_t *) vm_pop (vm));

  c = a - b;

  vm_push (vm, &c);
}

static void vmi_imul (vm_t *vm)
{
  int32_t a, b, c;
  b = *((int32_t *) vm_pop (vm));
  a = *((int32_t *) vm_pop (vm));

  c = a * b;

  vm_push (vm, &c);
}

static void vmi_idiv (vm_t *vm)
{
  int32_t a, b, c;
  b = *((int32_t *) vm_pop (vm));
  a = *((int32_t *) vm_pop (vm));

  c = a / b;

  vm_push (vm, &c);
}

vmi_t vm_fetch (vm_t *vm) {
  return VMI_IADD;
}

void vm_step (vm_t *vm)
{
  switch (vm_fetch (vm)) {
  case VMI_IADD: vmi_iadd (vm); break;
  case VMI_ISUB: vmi_isub (vm); break;
  case VMI_IMUL: vmi_imul (vm); break;
  case VMI_IDIV: vmi_idiv (vm); break;
  case VMI_CALL: break;
  }
}

void *vm_run (vm_t *vm)
{
  return NULL;
}


#ifdef TEST

#include <assert.h>
#include <stdio.h>

void test_stack0 ()
{
  vm_t vm;
  int32_t a, b, c = -1;

  a = 20;
  b = 30;

  vm_init (&vm);
  vm_push (&vm, &a);
  vm_push (&vm, &b);
  vmi_iadd (&vm);
  c = *((int32_t*) vm_pop (&vm));

  assert (c == 50);
  printf ("%d+%d=%d\n", a, b, c);
}

#endif
