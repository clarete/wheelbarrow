"""
# Basic API

  >>> m1 = Machine1()
  >>> m1.dump_stack()
  []

# PUSH <ARG>

  >>> m1.evaluate(['PUSH', 10])
  >>> m1.dump_stack()
  [10]

Just cleaning the stack for the next test

  >>> m1.evaluate(['POP'])

# POP

  >>> m1.evaluate(['PUSH', 10, 'POP'])
  >>> m1.dump_stack()
  []

# SUM

pops and sums the 2 topmost values on the stack and pushes the result.

  >>> m1.evaluate(['PUSH', 11, 'PUSH', 22, 'PUSH', 33, 'SUM'])
  >>> m1.dump_stack()
  [11, 55]

Just cleaning the stack for the next test

  >>> m1.evaluate(['POP', 'POP'])

# SUMX

let len be the topmost value popped from the stack: SUMX pops and sums
the top len values on the stack and pushes the result.

  >>> m1.evaluate(['PUSH', 4, 'PUSH', 5, 'PUSH', 6, 'PUSH', 3, 'SUMX'])
  >>> m1.dump_stack()
  [15]
"""

class Machine1:

    def __init__(self):
        self.stack = []
        self.stack_position = -1
        self.instruction_position = -1

    def dump_stack(self): return self.stack

    def push(self, value): self.stack.append(value)

    def pop(self): return self.stack.pop()

    def has_input(self, l): return self.instruction_position < len(l) -1

    def read(self, l):
        self.instruction_position += 1
        return l[self.instruction_position]

    def evaluate(self, input_list):
        while self.has_input(input_list):
            instruction = self.read(input_list)
            if instruction == 'PUSH':
                self.push(self.read(input_list))
            elif instruction == 'POP':
                self.pop()
            elif instruction == 'SUM':
                self.push(self.pop() + self.pop())
            elif instruction == 'SUMX':
                self.push(sum(self.pop() for i in range(self.pop())))
        self.instruction_position = -1


def test():
    m1 = Machine1()
    m1.evaluate(['PUSH', 10, 'POP'])
    print(m1.dump_stack())
    m1.evaluate(['PUSH', 11, 'PUSH', 22, 'PUSH', 33, 'SUM'])
    print(m1.dump_stack())
    m1.evaluate(['PUSH', 4, 'PUSH', 5, 'PUSH', 6, 'PUSH', 3, 'SUMX'])
    print(m1.dump_stack())

if __name__ == '__main__':
    test()
