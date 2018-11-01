all: bin

GAME		:= game
SRCS		:= main.c
OBJS		:= $(patsubst %.c,%.o,$(SRCS))

PKGCFGNAME	:= sdl2
CFLAGS		+= $(shell pkg-config --cflags $(PKGCFGNAME))
LDFLAGS		+= $(shell pkg-config --libs $(PKGCFGNAME))


# Relative to the current directory
DEPDIR		:= .d
# Handle header dependency. Huge thanks to the following article:
# http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/
DEPFLAGS	= -MT $@ -MMD -MP -MF $(DEPDIR)/$*.Td
CCC		= $(CC) $(DEPFLAGS) $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH)
COMPILE.c	= $(CCC) -c
POSTCOMPILE	= @mv -f $(DEPDIR)/$*.Td $(DEPDIR)/$*.d && touch $@

bin: $(GAME)
$(GAME): $(OBJS); $(CCC) $(LDFLAGS) -o $@ $^

# More on binary dependency
$(shell mkdir -p $(DEPDIR) >/dev/null)
$(DEPDIR)/%.d:;
.PRECIOUS: $(DEPDIR)/%.d
%.o: %.c
%.o: %.c
	$(COMPILE.c) $(OUTPUT_OPTION) $<
	$(POSTCOMPILE)
include $(wildcard $(patsubst %,$(DEPDIR)/%.d,$(SRCS)))
