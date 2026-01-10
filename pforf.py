# Interpreter for a forth-like language (not following any specific standards)
#                                        ^--(this is why it's forf not forth)

# TODO: add : and ; for coldef
# not big concerns: add doubles and the respective words for them

class Interpreter:
    def __init__(self):
        # the stack of the program, where the code is stored
        self.stack = []

        # stores the primitive words (functions)
        # defined as anonymous lambda functions
        # primitives implemented are based on the following list:
        # https://users.ece.cmu.edu/~koopman/stack_computers/appb.html
        # note: N1, N2, N3, etc are representing the stack like this:
        # first -> last items of stack
        # N1, N2, N3
        # third last, second last, last
        # also no type or error checking for now, you get what you get and you
        # don't get upset
        self.words = {
            # using 0 to represent false and non-zero to represent true
            # also x if cond else y is syntax for one line if statements
            "0<": lambda: self.stack.append(1 if self.stack.pop() < 0 else 0),
            "0>": lambda: self.stack.append(1 if self.stack.pop() < > else 0),
            "0=": lambda: self.stack.append(1 if self.stack.pop() == 0 else 0),
            "1+": lambda: self.stack.append(self.stack.pop() + 1),
            "1-": lambda: self.stack.append(self.stack.pop() - 1),
            "2+": lambda: self.stack.append(self.stack.pop() + 2),
            "2-": lambda: self.stack.append(self.stack.pop() - 2),
            # floor division
            "2/": lambda: self.stack.append(self.stack.pop() // 2),
            "4+": lambda: self.stack.append(self.stack.pop() + 4),
            "4-": lambda: self.stack.append(self.stack.pop() - 4),
            "<": lambda: self.stack.append(1 if self.stack.pop(-2) < self.stack.pop(-1) else 0),
            # inequality
            "<>": lambda: self.stack.append(1 if self.stack.pop(-2) != self.stack.pop(-1) else 0),
            # you'll never guess
            "=": lambda: self.stack.append(1 if self.stack.pop(-2) == self.stack.pop(-1) else 0),
            ">": lambda: self.stack.append(1 if self.stack.pop(-2) > self.stack.pop(-1) else 0),
            # there would be the R (literal) word here to add an address
            # to return stack but the interpreter uses a high level language and
            # "design" so it's not something i want to go out of my way for
            # also no words for controlling memory will be added
            "+": lambda: self.stack.append(self.stack.pop(-2) + self.stack.pop(-1)),
            "-": lambda: self.stack.append(self.stack.pop(-2) - self.stack.pop(-1)),
            # duplicates head if non-zero
            "?DUP": lambda: self.stack.append(self.stack[-1] if self.stack[-1] != 0 else None),
            "ABS": lambda: self.stack.append(abs(self.stack.pop())),
            "AND": lambda: self.stack.append(1 if self.stack.pop() == self.stack.pop() else 0)
        }

    # code is just whitespace separated so we can use split() to read it
