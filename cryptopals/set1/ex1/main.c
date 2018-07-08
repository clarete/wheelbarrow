/* http://cryptopals.com/sets/1/challenges/1 */

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

typedef struct {
  const char *input;
  int position;
} bp_t;

static int b64table[64] = {
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
  'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
  'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
  'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/',
};

void bpInit (bp_t *p, const char *input)
{
  p->input = input;
  p->position = 0;
}

char bpNib (bp_t *p, int index)
{
  char value = p->input[p->position + index];
  if (value >= 'a' && value <= 'f') value -= 55;
  return value & 0x0F;
}

void bpNext (bp_t *p)
{
  if (p->position % 3 == 0 && p->position != 0) {
    char third = bpNib(p, -1);
    char second = bpNib(p, -2);
    char first = bpNib(p, -3);
    printf ("%c", b64table[((first << 2) | second >> 2)]);
    printf ("%c", b64table[(((second << 4) & 0x3f) | (third & 0x0F))]);
  }
  p->position++;
}

void b64e (const char *input)
{
  bp_t p;
  bpInit (&p, input);

  for (size_t i = 0; i <= strlen (input); i++) {
    bpNext (&p);
  }
  printf ("\n");
}

int main()
{
  b64e ("49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d");
  return 0;
}
