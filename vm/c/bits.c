#include <stddef.h>
#include "bits.h"

void vmb_pack_word (code_t *buffer, size_t start, vmw_t byte)
{
  buffer[start] = byte;
}

vmw_t vmb_unpack_word (code_t *buffer, size_t start)
{
  return buffer[start];
}
