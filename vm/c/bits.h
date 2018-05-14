#ifndef BITS_H
#define BITS_H

#include <stddef.h>             /* for size_t */

typedef int code_t;

typedef unsigned long vmw_t;

void vmb_pack_word (code_t *buffer, size_t start, vmw_t byte);

vmw_t vmb_unpack_word (code_t *buffer, size_t start);


#endif  /* BITS_H */
