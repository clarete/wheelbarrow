#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define WORD_SIZE sizeof (uint16_t)
#define OPERATOR_SIZE sizeof (uint8_t)
#define OPERAND_SIZE sizeof (uint8_t)

#define OP_PUSH 0x1
#define OP_POP  0x2
#define OP_SUM  0x3
#define OP_SUMX 0x4

#define STACK_SIZE 2048

#define ERRMSG(e) (errorStr[e])

#define FATAL(e) do { printf ("%s\n", ERRMSG (e)); exit (EXIT_FAILURE); } while (0);


typedef struct {
  uint8_t stack[STACK_SIZE];
  uint8_t *sp;
  uint8_t *ip;
} Machine;

typedef enum {
  M2_OK = 0,
  M2_ERR_USAGE,
  M2_ERR_OPEN_FILE,
  M2_ERR_READ_FILE,
  M2_ERR_ALLOC_MEM,
  M2_ERR_UNKNOWN_INSTRUCTION,
  M2_ERR_END,
} Error;

static const char *errorStr[M2_ERR_END] = {
  [M2_OK] = "Great success",
  [M2_ERR_USAGE] = "Usage: machine2 <filename.m2>",
  [M2_ERR_OPEN_FILE] = "Can't open file",
  [M2_ERR_READ_FILE] = "Can't read file",
  [M2_ERR_ALLOC_MEM] = "Can't allocate memory",
  [M2_ERR_UNKNOWN_INSTRUCTION] = "Unknown instruction",
};

#define NEXT(m)    (*(m)->ip++)
#define PUSH(m,x)  (*(m)->sp++ = (x))
#define POP(m)     (*--(m)->sp)

void mInit (Machine *m, uint8_t *code)
{
  memset (m->stack, 0, sizeof (uint8_t) * STACK_SIZE);
  m->sp = m->stack;
  m->ip = code;
}

void mEval (Machine *m)
{
  uint8_t instruction, argument;
  while (true) {
    instruction = NEXT (m);
    argument = NEXT (m);
    switch (instruction) {

    case 0x0: return;           /* HALT */

    case OP_PUSH:
      /* printf ("push %d\n", argument); */
      PUSH (m, argument);
      break;

    case OP_POP:
      /* printf ("pop\n"); */
      (void) POP (m);
      break;

    case OP_SUM: {
      /* printf ("sum\n"); */
      uint8_t b = POP (m);
      uint8_t a = POP (m);
      PUSH (m, a + b);
    } break;

    case OP_SUMX: {
      /* printf ("sumx\n"); */
      uint8_t len = POP (m);
      uint8_t total = 0;
      for (int i = 0; i < len; i++) total += POP (m);
      PUSH (m, total);
    } break;

    default: FATAL (M2_ERR_UNKNOWN_INSTRUCTION);
    }
  }
}

void mDumpStack (Machine *m)
{
  uint8_t *sp;
  sp = m->sp;
  printf ("[");
  while (*--sp) {
    printf ("%hhu", *sp);
    if (*(sp - 1)) printf (", ");
  }
  printf ("]\n");
}

Error loadFile (const char *fname, uint8_t **buffer, long *fsize)
{
  long read;
  FILE *f = fopen (fname, "rb");
  if (f == NULL) return M2_ERR_OPEN_FILE;

  /* Read file size */
  fseek (f, 0, SEEK_END);
  *fsize = ftell (f);
  rewind (f);

  /* Allocate buffer for code */
  *buffer = (uint8_t *) calloc (*fsize, sizeof (uint8_t));
  if (buffer == NULL) return M2_ERR_ALLOC_MEM;

  /* Read bytecode into memory */
  read = fread (*buffer, sizeof (uint8_t), *fsize, f);
  fclose (f);
  if (read != *fsize) FATAL (M2_ERR_READ_FILE);

  return M2_OK;
}

void printBuffer (const uint8_t *data, long fsize)
{
  for (long i = 0; i < fsize; i++) printf ("%x ", (unsigned int) data[i]);
  printf ("\n");
}

int main (int argc, char **argv)
{
  Machine m;
  Error e;
  uint8_t *buffer = NULL;
  long bsize;

  if (argc != 2) FATAL (M2_ERR_USAGE);

  if ((e = loadFile (argv[1], &buffer, &bsize)) != M2_OK) FATAL (e);

  if (buffer == NULL) FATAL (e);

  /* printBuffer (buffer, bsize); */

  mInit (&m, buffer);
  mEval (&m);
  mDumpStack (&m);

  free (buffer);

  return 0;
}
