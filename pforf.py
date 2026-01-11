# Interpreter for a forth-like language (not following any specific standards)
#                                        ^--(this is why it's forf not forth)

# TODO: add : and ; for coldef
# not big concerns: add doubles and the respective words for them

class Pforf:
    def __init__(self):
        # the stack of the program, where the code is stored
        self.stack = []
        # instruction pointer for branching
        self.ip = 0
        # the tokens made from code
        self.tokens = []

        # stores the primitive words (functions)
        # primitives implemented are based on the following list:
        # https://users.ece.cmu.edu/~koopman/stack_computers/appb.html
        # note: N1, N2, N3, etc are representing the stack like this:
        # first -> last items of stack
        # N1, N2, N3
        # third last, second last, last
        # also no type or error checking for now, you get what you get and you
        # don't get upset
        self.dictionary = {
            # using 0 to represent false and non-zero to represent true
            # also x if cond else y is syntax for one line if statements
            "0<": lambda: self.stack.append(1 if self.stack.pop() < 0 else 0),
            "0>": lambda: self.stack.append(1 if self.stack.pop() > 0 else 0),
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
            # also a cool trick to append conditionally i got from ai
            "?DUP": lambda: self.stack[-1] != 0 and self.stack.append(self.stack[-1]),
            "ABS": lambda: self.stack.append(abs(self.stack.pop())),
            "AND": lambda: self.stack.append(1 if self.stack.pop() == self.stack.pop() else 0),
            "IF": lambda: self.ifWord(),
            # THEN is handled by IF
            "THEN": lambda: self.thenWord(),
            "ELSE": lambda: None,
        }

    def ifWord(self):
        searchArea = self.tokens[self.ip:]
        if self.stack.pop() == 0:
            # there's probably a more elegant/sensible way to keep track of
            # current index and token
            index = 0
            for token in searchArea:
                if token == "ELSE" or token == "THEN":
                    self.ip += index
                    return
                index += 1
            raise SyntaxError(f"Incomplete if statement at token #{index}.")
        # no need to check for truth since reaching THEN will skip ELSE

    def thenWord(self):
        searchArea = self.tokens[self.ip:]
        index = 0
        for token in searchArea:
            if token == "ELSE":
                self.ip += index
                return
            index += 1

    def run(self, code):
        self.ip = 0
        self.stack = []
        # code is just whitespace separated so we can use split() to read it
        self.tokens = code.split()
        while self.ip < len(self.tokens):
            token = self.tokens[self.ip]
            if token in self.dictionary:
                self.dictionary[token]()
            else:
                try:
                    # type check later, adds unrecognised tokens as floats
                    self.stack.append(float(token))
                except ValueError:
                    raise SyntaxError(f"Unknown word: {token}")
            self.ip += 1

        # old loop
        # for token in tokens:
        #     if token in self.dictionary:
        #         self.dictionary[token]()
        #     else:
        #         try:
        #             # type check later, adds unrecognised tokens as floats
        #             self.stack.append(float(token))
        #         except ValueError:
        #             print(f"Unknown word: {token}")
        # just print the stack at the end for now
        print(self.stack)
