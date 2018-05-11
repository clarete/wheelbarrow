#ifndef VM_H
#define VM_H

#include <stdint.h>

#define STACK_SIZE 2048

typedef struct {
  void *stack[STACK_SIZE];
  int32_t stack_pointer;
} vm_t;

typedef unsigned long vmw_t;

typedef enum {
  VMI_IADD,
  VMI_ISUB,
  VMI_IMUL,
  VMI_IDIV,
  VMI_CALL,
} vmi_t;

/* What is needed for using the VM */
void vm_init (vm_t *vm);
void *vm_run (vm_t *vm);

/* What vm uses to run itself */
vmi_t vm_fetch (vm_t *vm);
void vm_step (vm_t *vm);

/* Stack */
void vm_push (vm_t *vm, void *i);
void *vm_pop (vm_t *vm);

/* Bytecode Generator */
vmw_t gen_opc (vmi_t opc);
vmw_t gen_int (int v);
vmw_t gen_float (float v);
vmw_t gen_string ();
vmw_t gen_call ();

#endif  /* VM_H */
