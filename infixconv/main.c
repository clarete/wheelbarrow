#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

typedef enum {
  TOKEN_ADD,
  TOKEN_SUB,
  TOKEN_DIV,
  TOKEN_MUL,
  TOKEN_OP,
  TOKEN_CP,
  TOKEN_NUM,
  TOKEN_END,
} TokenType;

const char TokenTypeNames[][TOKEN_END] = {
  "ADD",
  "SUB",
  "DIV",
  "MUL",
  "OP",
  "CP",
  "NUM",
};

typedef struct {
  TokenType type;
  union {
    const char *string;
    int integer;
    long longint;
  } as;
} Token;

typedef struct {
  int cursor;
  int inputSize;
  const char *input;
  Token token;
} Context;

void eatWhiteSpaces (Context *c)
{
  /* Parse whitespace */
  while (isspace (c->input[c->cursor]))
    c->cursor++;
}

void nextToken (Context *c)
{
  eatWhiteSpaces (c);

  /* Parse Operands */
  switch (c->input[c->cursor]) {
  case '(':
    c->token = (Token){ .type = TOKEN_OP };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  case ')':
    c->token = (Token){ .type = TOKEN_CP };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  case '+':
    c->token = (Token){ .type = TOKEN_ADD };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  case '-':
    c->token = (Token){ .type = TOKEN_SUB };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  case '*':
    c->token = (Token){ .type = TOKEN_MUL };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  case '/':
    c->token = (Token){ .type = TOKEN_DIV };
    c->cursor++;
    eatWhiteSpaces (c);
    return;
  }

  /* Parse Digits */
  int pos = c->cursor;
  while (isdigit (c->input[pos]))
    pos++;
  if (pos > c->cursor) {
    char arr[pos - c->cursor];
    strncpy (arr, c->input + c->cursor, pos);
    c->cursor = pos;
    int value = atoi (arr);
    c->token = (Token){
      .type = TOKEN_NUM,
      .as = { .integer = value }
    };
  }
  eatWhiteSpaces (c);
}

void parse (Context *c)
{
  do {
    printf ("[Pos %02d] ", c->cursor);
    nextToken (c);
    printf ("Found Token: %s", TokenTypeNames[c->token.type]);
    if (c->token.type == TOKEN_NUM)
      printf ("(%d)", c->token.as.integer);
    printf ("\n");
  } while (c->cursor < c->inputSize);
}

void convert (const char *expr, size_t size)
{
  Context c;
  c.input = expr;
  c.inputSize = size;
  c.cursor = 0;
  parse (&c);
}

void usage (const char *prog)
{
  fprintf (stderr, "Usage: %s INPUT\n", prog);
}

int main (int argc, char **argv)
{
  if (argc != 2) {
    usage (argv[0]);
    return EXIT_FAILURE;
  } else {
    convert (argv[1], strlen (argv[1]));
    return EXIT_SUCCESS;
  }
}
