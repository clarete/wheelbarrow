#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define WORD_SIZE  sizeof (Word)
#define STACK_SIZE 2048

#define OP_PUSH  0x1
#define OP_POP   0x2
#define OP_SUM   0x3
#define OP_SUMX  0x4
#define OP_PCALL 0x5

#define WTOI(x) ((uint8_t) (uintptr_t) (x))
#define ITOW(x) ((Word) (uintptr_t) (x))

#define ERRMSG(e) (errorStr[e])

#define FATAL(e) do { printf ("%s\n", ERRMSG (e)); exit (EXIT_FAILURE); } while (0);

typedef void* Word;

typedef uint8_t Bytecode;

typedef struct {
  Word stack[STACK_SIZE];
  Word *sp;
  Bytecode *ip;
} Machine;

typedef enum {
  M2_OK = 0,
  M2_ERR_USAGE,
  M2_ERR_OPEN_FILE,
  M2_ERR_READ_FILE,
  M2_ERR_ALLOC_MEM,
  M2_ERR_UNKNOWN_INSTRUCTION,
  M2_ERR_UNKNOWN_PRIMITIVE,
  M2_ERR_WRONG_ARITY,
  M2_ERR_END,
} Error;

static const char *errorStr[M2_ERR_END] = {
  [M2_OK] = "Great success",
  [M2_ERR_USAGE] = "Usage: machine2 <filename.m2>",
  [M2_ERR_OPEN_FILE] = "Can't open file",
  [M2_ERR_READ_FILE] = "Can't read file",
  [M2_ERR_ALLOC_MEM] = "Can't allocate memory",
  [M2_ERR_UNKNOWN_INSTRUCTION] = "Unknown instruction",
  [M2_ERR_UNKNOWN_PRIMITIVE] = "Unknown primitive",
  [M2_ERR_WRONG_ARITY] = "Wrong arity",
};

#define PUSH(m,x)  (*(m)->sp++ = (x))
#define POP(m)     (*--(m)->sp)

void mInit (Machine *m, Word code)
{
  memset (m->stack, 0, STACK_SIZE * WORD_SIZE);
  m->sp = m->stack;
  m->ip = code;
}

void primPrint (Machine *m)
{
  Word obj, argc = POP (m);
  if (WTOI (argc) != 1) FATAL (M2_ERR_WRONG_ARITY);

  obj = POP (m);

  printf ("%hhu\n", WTOI (obj));

  PUSH (m, 0);
}

Word decode (Bytecode *b)
{
  uint8_t word = 0;
  word += WTOI (b[0]);
  word += WTOI (b[1]) << 8;
  return ITOW (word);
}

void mReadOpc (Machine *m, Word *instruction, Word *argument)
{
  *instruction = decode (m->ip++);
  *argument = decode (m->ip++);
}

void mEval (Machine *m)
{
  Word instruction, argument;
  while (true) {
    mReadOpc (m, &instruction, &argument);

    switch (WTOI (instruction)) {

    case 0x0: return;           /* HALT */

    case OP_PUSH:
      /* printf ("[0x%x] push %d\n", WTOI (instruction), WTOI (argument)); */
      PUSH (m, argument);
      break;

    case OP_POP:
      /* printf ("pop\n"); */
      (void) POP (m);
      break;

    case OP_SUM: {
      /* printf ("sum\n"); */
      Word b = POP (m);
      Word a = POP (m);
      PUSH (m, ITOW (WTOI (a) + WTOI (b)));
    } break;

    case OP_SUMX: {
      /* printf ("sumx\n"); */
      uint8_t len = WTOI (POP (m));
      uint8_t total = 0;
      for (int i = 0; i < len; i++) total += WTOI (POP (m));
      PUSH (m, ITOW (total));
    } break;

    case OP_PCALL: {
      if (WTOI (argument) == 255) primPrint (m);
      else FATAL (M2_ERR_UNKNOWN_PRIMITIVE);
    } break;

    default: FATAL (M2_ERR_UNKNOWN_INSTRUCTION);
    }
  }
}

void mDumpStack (Machine *m)
{
  Word *sp;
  sp = m->sp;
  printf ("[");
  while (sp-- > m->stack) {
    printf ("%hhu", WTOI (*sp));
    if (sp - 1 > m->stack) printf (", ");
  }
  printf ("]\n");
}

Error loadFile (const char *fname, Bytecode **buffer, long *fsize)
{
  long read;
  FILE *f = fopen (fname, "rb");
  if (f == NULL) return M2_ERR_OPEN_FILE;

  /* Read file size */
  fseek (f, 0, SEEK_END);
  *fsize = ftell (f);
  rewind (f);

  /* Allocate buffer for code */
  *buffer = (Bytecode *) calloc (*fsize, WORD_SIZE);
  if (buffer == NULL) return M2_ERR_ALLOC_MEM;

  /* Read bytecode into memory */
  read = fread (*buffer, sizeof (uint8_t), *fsize, f);
  fclose (f);
  if (read != *fsize) FATAL (M2_ERR_READ_FILE);

  return M2_OK;
}

int main (int argc, char **argv)
{
  Machine m;
  Error e;
  Bytecode *buffer = NULL;
  long bsize;

  if (argc != 2) FATAL (M2_ERR_USAGE);

  if ((e = loadFile (argv[1], &buffer, &bsize)) != M2_OK) FATAL (e);

  if (buffer == NULL) FATAL (e);

  mInit (&m, buffer);
  mEval (&m);
  mDumpStack (&m);

  free (buffer);

  return 0;
}
