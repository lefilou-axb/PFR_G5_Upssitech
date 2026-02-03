#ifndef INTERPRETER_H
#define INTERPRETER_H

#include "types.h"

int interpret_words(word_t words[],
                    int n,
                    command_t commands[]);

#endif
