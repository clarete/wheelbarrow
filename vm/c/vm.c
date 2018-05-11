#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "vm.h"

#define ERROR_STACK_OVERFLOW  51
#define ERROR_STACK_UNDERFLOW 52
#define ERROR_UNKNOWN_OPCODE  53

/* Forward declaration for instructions */

/* Integer */
static inline void vmi_iadd (vm_t *vm);
static inline void vmi_isub (vm_t *vm);
static inline void vmi_imul (vm_t *vm);
static inline void vmi_idiv (vm_t *vm);
/* Float */
/* static inline void vmi_fadd (vm_t *vm); */
/* static inline void vmi_fsub (vm_t *vm); */
/* static inline void vmi_fmul (vm_t *vm); */
/* static inline void vmi_fdiv (vm_t *vm); */
/* Symbols */
static inline void vmi_istore (vm_t *vm, int32_t i);
/* static inline void vmi_fstore (vm_t *vm); */
static inline void vmi_iload (vm_t *vm);
/* static inline void vmi_fload (vm_t *vm); */
/* Jumps */
static inline void vmi_jz (vm_t *vm);
static inline void vmi_jmp (vm_t *vm);
static inline void vmi_jmpb (vm_t *vm);
/* Callables */
static inline void vmi_call (vm_t *vm);
/* Return */
static inline void vmi_ret (vm_t *vm);

#define VMI_NAME(n) (VMI_NAMES[n])

/* Should be kept in sync with `vmi_t' in vm.h */
static const char *VMI_NAMES[VMIE] = {
  [VMI_IADD] = "VMI_IADD",
  [VMI_ISUB] = "VMI_ISUB",
  [VMI_IMUL] = "VMI_IMUL",
  [VMI_IDIV] = "VMI_IDIV",

  [VMI_ISTORE] = "VMI_ISTORE",
  [VMI_ILOAD] = "VMI_ILOAD",

  [VMI_JZ] = "VMI_JZ",
  [VMI_JMP] = "VMI_JMP",
  [VMI_JMPB] = "VMI_JMPB",

  [VMI_CALL] = "VMI_CALL",
  [VMI_RET] = "VMI_RET",
};

static void print_obj (obj_t *obj)
{
  switch (obj->type) {
  case OBJ_INT: printf ("%d", obj->intval); break;
  }
}

obj_t *vm_new_obj (vm_t *vm, obj_type_t type)
{
  obj_t *obj = malloc (sizeof (obj_t));
  obj->marked = 0;
  obj->type = type;

  obj->next = vm->objs;
  vm->objs = obj;
  return obj;
}

void vm_init (vm_t *vm)
{
  vm->objs = NULL;
  vm->stack_pointer = 0;
  memset (vm->stack, 0, STACK_MAX_SIZE * sizeof (obj_t *));
}

void vm_push (vm_t *vm, obj_t *i)
{
  if (vm->stack_pointer >= STACK_MAX_SIZE)
    exit (ERROR_STACK_OVERFLOW);
  vm->stack[vm->stack_pointer++] = i;
}

void vm_push_int (vm_t *vm, int32_t value)
{
  obj_t *int_obj = vm_new_obj (vm, OBJ_INT);
  int_obj->intval = value;
  vm_push (vm, int_obj);
}

obj_t *vm_pop (vm_t *vm)
{
  if (vm->stack_pointer <= 0)
    exit (ERROR_STACK_UNDERFLOW);
  return vm->stack[--vm->stack_pointer];
}

static void vmi_iadd (vm_t *vm)
{
  obj_t *a = NULL, *b = NULL;
  b = vm_pop (vm);
  a = vm_pop (vm);
  vm_push_int (vm, a->intval + b->intval);
}

static void vmi_isub (vm_t *vm)
{
  obj_t *a, *b;
  b = vm_pop (vm);
  a = vm_pop (vm);
  vm_push_int (vm, a->intval - b->intval);
}

static void vmi_imul (vm_t *vm)
{
  obj_t *a, *b;
  b = vm_pop (vm);
  a = vm_pop (vm);
  vm_push_int (vm, a->intval * b->intval);
}

static void vmi_idiv (vm_t *vm)
{
  obj_t *a, *b;
  b = vm_pop (vm);
  a = vm_pop (vm);
  vm_push_int (vm, a->intval / b->intval);
}

static void vmi_istore (vm_t *vm, int32_t i)
{
  printf ("ISTORE: %d\n", i);
  vm_push_int (vm, i);
}

static void vmi_iload (vm_t *vm)
{
}

static void vmi_jz (vm_t *vm)
{
}

static void vmi_jmp (vm_t *vm)
{
}

static void vmi_jmpb (vm_t *vm)
{
}

static void vmi_call (vm_t *vm)
{
}

static void vmi_ret (vm_t *vm)
{
}

void *vm_run (vm_t *vm, char *buffer, size_t len)
{
  size_t rcursor = 0;
  vmi_t opc;
  int32_t int_value;

  while (rcursor < len) {
    rcursor += vmb_read_opc (buffer, rcursor, &opc);
    printf ("OPC: %s\n", VMI_NAME (opc));

    switch (opc) {
    case VMI_IADD: vmi_iadd (vm); break;
    case VMI_ISUB: vmi_isub (vm); break;
    case VMI_IMUL: vmi_imul (vm); break;
    case VMI_IDIV: vmi_idiv (vm); break;
    case VMI_ISTORE: {
      rcursor += vmb_read_int (buffer, rcursor, &int_value);
      printf ("IVAL: %d\n", int_value);
      vm_push_int (vm, int_value);
      /* vmi_istore (vm, int_value); */
      break;
    }
    case VMI_ILOAD: vmi_iload (vm); break;
    case VMI_JZ: vmi_jz (vm); break;
    case VMI_JMP: vmi_jmp (vm); break;
    case VMI_JMPB: vmi_jmpb (vm); break;
    case VMI_CALL: vmi_call (vm); break;
    case VMI_RET: vmi_ret (vm); break;
    default: exit (ERROR_UNKNOWN_OPCODE);
    }
  }
  return NULL;
}

size_t vmb_write_int (char *buffer, size_t start, int i)
{
  vmb_pack_word (buffer, start, i | 0x8000000000000000);
  return 1;
}

size_t vmb_read_int (char *buffer, size_t position, int *value)
{
  vmw_t word = vmb_unpack_word (buffer, position);
  *value = word & 0x7FFFFFFFFFFFFFFF;
  return 1;
}

size_t vmb_write_opc (char *buffer, size_t start, vmi_t opc) {
  vmb_pack_word (buffer, start, opc);
  return 1;
}

size_t vmb_read_opc (char *buffer, size_t position, vmi_t *value)
{
  *value = vmb_unpack_word (buffer, position);
  return 1;
}

#ifdef TEST

#include <assert.h>
#include <stdio.h>

void test_bytecode0 ()
{
  char *buffer = malloc (20);
  size_t wcursor = 0, rcursor = 0;
  obj_t *result = NULL;

  vmi_t opc;
  int int_value;

  vm_t vm;

  wcursor += vmb_write_opc (buffer, wcursor, VMI_ISTORE);
  wcursor += vmb_write_int (buffer, wcursor, 2);
  wcursor += vmb_write_opc (buffer, wcursor, VMI_ISTORE);
  wcursor += vmb_write_int (buffer, wcursor, 3);
  wcursor += vmb_write_opc (buffer, wcursor, VMI_IADD);

  rcursor += vmb_read_opc (buffer, rcursor, &opc);
  printf ("FIRST OPC: %s\n", VMI_NAME (opc));
  rcursor += vmb_read_int (buffer, rcursor, &int_value);
  printf ("FIRST VALUE: %d\n", int_value);
  rcursor += vmb_read_opc (buffer, rcursor, &opc);
  printf ("SECOND OPC: %s\n", VMI_NAME (opc));
  rcursor += vmb_read_int (buffer, rcursor, &int_value);
  printf ("SECOND VALUE: %d\n", int_value);
  rcursor += vmb_read_opc (buffer, rcursor, &opc);
  printf ("THIRD OPC: %s\n", VMI_NAME (opc));

  rcursor = 0;
  printf ("VM_RUN() ---- \n");

  vm_init (&vm);
  vm_run (&vm, buffer, wcursor);

  result = vm_pop (&vm);
  printf ("RESULT: ");
  print_obj (result);
  printf ("\n");
}

void test_stack0 ()
{
  vm_t vm;
  obj_t *result;

  vm_init (&vm);
  vm_push_int (&vm, 20);
  vm_push_int (&vm, 30);
  vmi_iadd (&vm);
  result = vm_pop (&vm);

  /* assert (result == 50); */
  printf ("20+30=");
  print_obj (result);
  printf ("\n");
}

#endif
