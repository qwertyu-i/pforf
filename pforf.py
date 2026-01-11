# Interpreter for a forth-like language (not following any specific standards)
#                                        ^--(this is why it's forf not forth)

#TODO: evaluation function, coldef

class Pforf:
    def __init__(self):
        # the stack of the program, where the code is stored
        self.stack = []
        # instruction pointer for branching
        self.ip = 0
        # the tokens made from code
        self.tokens = []
        # Added: stack to handle nested loops (index, limit, start_ip)
        self.loop_stack = []

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
            "IF": self.ifWord,
            # THEN is handled by IF
            "THEN": self.thenWord,
            "ELSE": lambda: None, # terminator
            "DO": self.doWord,
            "LOOP": self.loopWord,
            "I": self.iWord
        }

    def skip_until(self, targets):
        # increase when we find another if since we don't want to end early
        depth = 0
        while self.ip < len(self.tokens) - 1:
            self.ip += 1
            token = self.tokens[self.ip]

            # Track depth for nesting (IFs and DOs)
            if token in ["IF", "DO"]:
                depth += 1
            elif token == "ELSE":
                if depth == 0 and "ELSE" in targets:
                    return
                depth -= 1
            elif token == "THEN":
                if depth == 0 and "THEN" in targets:
                    return
            elif token == "LOOP":
                depth -= 1

        raise SyntaxError(f"Missing terminator {targets}")

    def ifWord(self):
        if self.stack.pop() == 0:
            self.skip_until(["THEN", "ELSE"])

    def thenWord(self):
        self.skip_until(["ELSE"])

    def doWord(self):
        index = self.stack.pop()
        limit = self.stack.pop()
        # Save the loop state on a stack for nesting
        self.loop_stack.append({
            "index": index,
            "limit": limit,
            "start": self.ip + 1
        })

    def iWord(self):
        if not self.loop_stack:
            raise SyntaxError("I used outside of a loop")
        self.stack.append(self.loop_stack[-1]["index"])

    def loopWord(self):
        if not self.loop_stack:
            raise SyntaxError("LOOP without DO")
        
        loop = self.loop_stack[-1]
        loop["index"] += 1
        
        if loop["index"] < loop["limit"]:
            # -1 because run method will add 1 immediately
            self.ip = loop["start"] - 1
        else:
            self.loop_stack.pop()

    def run(self, code):
        self.ip = 0
        self.stack = []
        self.loop_stack = []
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

        # just print the stack at the end for now
        print(self.stack)
