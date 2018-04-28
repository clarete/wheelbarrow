#include <stdlib.h>
#include <string.h>
#include <stdio.h>

enum item_type {
  str_type,
  lst_type,
};

struct list {
  enum item_type type;
  char key;

  union {
    char *str;
    struct list *lst;
  };

  struct list *next;
};

struct list *append_str (struct list *l, char k, char *v)
{
  struct list *item = malloc (sizeof (struct list));
  item->type = str_type;
  item->key = k;
  item->str = v;
  item->next = l;
  return item;
}

struct list *append_lst (struct list *l, char k, struct list *v)
{
  struct list *item = malloc (sizeof (struct list));
  item->type = lst_type;
  item->key = k;
  item->lst = v;
  item->next = l;
  return item;
}

struct list *lookup (struct list *l, char k)
{
  if (!l) return NULL;
  if (l->key == k) return l;
  return lookup (l->next, k);
}

void fill (const char *t, struct list *env)
{
  struct list *result;
  if      (t[0] == '\0') return;
  else if (t[0] == '$') {
    result = lookup (env, t[1]);
    printf ("%s", result->str);
    fill (t+2, env);
  } else if (t[0] == '@') {
    result = lookup (env, t[1]);
    for (struct list *tmp = result->lst; tmp; tmp = tmp->next) {
      printf ("%s", tmp->str);
      if (tmp->next) printf (" and ");
    }
    fill (t+2, env);
  } else {
    printf ("%c", t[0]);
    fill (t+1, env);
  }
}

void free_lst (struct list *l)
{
  struct list *tmp, *i;
  if (!l) return;
  else if (l->type == lst_type) free_lst (l->lst);
  for (i = l; i;) {
    tmp = i->next;
    free (i);
    i = tmp;
  }
}

void test_base_stuff (struct list *env)
{
  struct list *result = lookup (env, 'x');
  printf ("Lookup X: %s\n", result->str);

  struct list *result2 = lookup (env, 'y');
  printf ("Lookup Y:\n");
  for (struct list *tmp = result2->lst; tmp; tmp = tmp->next) {
    printf (" * %s\n", tmp->str);
  }
}

int main()
{

  char *eg_template = "To understand $x you must first understand @y.";

  struct list *values = NULL;
  values = append_str (values, 0, "base cases");
  values = append_str (values, 0, "recursion");

  struct list *eg_env = NULL;
  eg_env = append_str (eg_env, 'x', "recursion");
  eg_env = append_lst (eg_env, 'y', values);

  /* -- Just making sure basic tools actually work! -- */
  /* test_base_stuff (eg_env); */

  fill (eg_template, eg_env);
  printf ("\n");

  free_lst (eg_env);

  return 0;
}
