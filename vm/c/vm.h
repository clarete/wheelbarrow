#ifndef VM_H
#define VM_H

#include <stddef.h>             /* for size_t */
#include <stdint.h>

#include "bits.h"

#define STACK_MAX_SIZE 4096

typedef enum {
  OBJ_INT,
  /* OBJ_FLOAT, */
} obj_type_t;

typedef struct object {
  obj_type_t type;

  /* Properties used by the GC */
  short int marked;
  struct object *next;

  /* Value Container */
  union {
    /* OBJ_INT */
    int32_t intval;
    /* OBJ_FLOAT */
    /* float floatval; */
  };
} obj_t;

typedef struct {
  obj_t *stack[STACK_MAX_SIZE];
  obj_t *objs;
  int32_t stack_pointer;
} vm_t;

typedef enum {
  /* Integer Math Ops */
  VMI_IADD,
  VMI_ISUB,
  VMI_IMUL,
  VMI_IDIV,

  /* Float Math Ops */
  /* VMI_FADD, */
  /* VMI_FSUB, */
  /* VMI_FMUL, */
  /* VMI_FDIV, */

  /* Store Symbols */
  VMI_ISTORE,
  /* VMI_FSTORE, */

  /* Load Symbols */
  VMI_ILOAD,
  /* VMI_FLOAD, */

  /* Jumps */
  VMI_JZ,
  VMI_JMP,
  VMI_JMPB,

  /* Callables */
  VMI_CALL,

  /* Return */
  VMI_RET,

  /* SENTINEL */
  VMIE,
} vmi_t;

/* What is needed for using the VM */
void vm_init (vm_t *vm);
void *vm_run (vm_t *vm, char *b, size_t l);

/* Stack */
void vm_push (vm_t *vm, obj_t *i);
obj_t *vm_pop (vm_t *vm);

/* Bytecode Generator */
size_t vmb_write_opc (char *b, size_t s, vmi_t v);
size_t vmb_write_int (char *b, size_t s, int v);
size_t vmb_write_float (char *b, size_t s, float v);
size_t vmb_write_string (char *b, size_t s, char *v);
/* void vmb_write_call (vmfn_t *v); */

/* Bytecode Reader */
size_t vmb_read_int (char *buffer, size_t position, int *value);
size_t vmb_read_opc (char *buffer, size_t position, vmi_t *value);

#endif  /* VM_H */
