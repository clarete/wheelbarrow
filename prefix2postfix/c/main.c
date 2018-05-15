#include <assert.h>
#include <stdio.h>
#include <string.h>

#define isoperator(x) (x == '+' || x == '-' || x == '*' || x == '/')

void prefix2postfix (const char *input, char *output)
{
  int output_cursor = 0;
  int top = -1;
  char stack[100];
  char a, b;

  for (int i = strlen (input)-1; i >= 0; i--) {
    if (!isoperator (input[i])) {
      stack[++top] = input[i];
    } else {
      b = stack[top--];
      if (top >= -1) a = stack[top--];
      if (top >= -1) output[output_cursor++] = a;
      output[output_cursor++] = b;
      output[output_cursor++] = input[i];
    }
  }
}

static void test0 ()
{
  const char *input = "*2+53";
  char output[100] = { 0 };
  prefix2postfix (input, output);
  printf ("output: %s\n", output);
  assert (strcmp (output, "35+2*") == 0);
}

int main ()
{
  test0 ();
  return 0;
}
