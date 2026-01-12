# Interpreter for a forth-like language (not following any specific standards)
#                                        ^--(this is why it's forf not forth)

# for getting files
import sys

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
            "2*": lambda: self.stack.append(self.stack.pop() * 2),
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
            # not floor division
            "/": lambda: self.stack.append(self.stack.pop(-2) / self.stack.pop(-1)),
            "*": lambda: self.stack.append(self.stack.pop() * self.stack.pop()),
            "SWAP": self.swapWord,
            # duplicates head if non-zero
            # also a cool trick to append conditionally i got from ai
            "?DUP": lambda: self.stack[-1] != 0 and self.stack.append(self.stack[-1]),
            "DUP": lambda: self.stack.append(self.stack[-1]),
            "ABS": lambda: self.stack.append(abs(self.stack.pop())),
            "AND": lambda: self.stack.append(1 if self.stack.pop() == self.stack.pop() else 0),
            "OR": lambda: self.stack.append(1 if self.stack.pop() == True or self.stack.pop() == True else 0),
            "IF": self.ifWord,
            "THEN": lambda: None,
            "ELSE": self.elseWord,
            "DO": self.doWord,
            "LOOP": self.loopWord,
            "LEAVE": self.leaveWord,
            "I": self.iWord,
            ":": self.colWord,
            ";": lambda: None,
            ".\"": self.quoteWord,
            "\"": None,
            ".": lambda: print(self.stack.pop(), end = ""),
            "CR": lambda: print(),
            "SPACE": lambda: print(" ", end = "")
        }

        # definitions will be "WORD: thread"
        # this takes priority over primitives
        self.wordDictionary = {}


    def swapWord(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a)
        self.stack.append(b)

    def skip_until(self, targets):
        depth = 0
        while self.ip < len(self.tokens) - 1:
            self.ip += 1
            token = self.tokens[self.ip]

            # correct LOOP has depth of -1
            if token in targets and (depth == 0 or (token == "LOOP" and depth == -1)):
                return

            # track depth
            if token in ["IF", "DO"]:
                depth += 1
            elif token == "THEN":
                depth -= 1
            elif token == "LOOP":
                depth -= 1

        raise SyntaxError(f"Missing terminator {targets}")

    def ifWord(self):
        if self.stack.pop() == 0:
            self.skip_until(["ELSE"])

    def elseWord(self):
        self.skip_until(["THEN"])

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

    def leaveWord(self):
        if not self.loop_stack:
            raise SyntaxError("No LOOP to LEAVE")
        self.loop_stack.pop()
        self.skip_until(["LOOP"])

    def colWord(self):
        self.ip += 1
        if self.ip >= len(self.tokens):
            raise SyntaxError("Expected word name after ':'")
        
        word_name = self.tokens[self.ip]
        definition = []
        
        self.ip += 1
        while self.ip < len(self.tokens):
            token = self.tokens[self.ip]
            if token == ";":
                self.wordDictionary[word_name] = definition
                return
            definition.append(token)
            self.ip += 1
            
        raise SyntaxError("Missing ';' in colon definition")

    def execute_tokens(self, tokens_to_run):
        old_tokens = self.tokens
        old_ip = self.ip
        
        # treat this as a new "file" while keeping data stack
        self.tokens = tokens_to_run
        self.ip = 0
        
        while self.ip < len(self.tokens):
            token = self.tokens[self.ip]
            self.evaluate_token(token)
            self.ip += 1
            
        # Restore state
        self.tokens = old_tokens
        self.ip = old_ip

    def evaluate_token(self, token):
        if token in self.wordDictionary:
            # keeps going until primitives reached
            self.execute_tokens(self.wordDictionary[token])
        elif token in self.dictionary:
            self.dictionary[token]()
        else:
            try:
                if "." in token:
                    self.stack.append(float(token))
                else:
                    self.stack.append(int(token))
            except ValueError:
                raise SyntaxError(f"Unknown word: {token}")

    def quoteWord(self):
        self.ip += 1
        start_ip = self.ip
        
        # go through until finding the ending word, because
        # forth likes to have the first quote as a word by itself
        # then the ending quote as part of the last word??
        # so we have to check the end of each token
        while self.ip < len(self.tokens):
            if self.tokens[self.ip].endswith('"'):
                full_string = " ".join(self.tokens[start_ip : self.ip + 1])
                self.stack.append(full_string.rstrip('"'))
                return
            self.ip += 1
            
        raise SyntaxError("Missing closing quote for string")

    def run(self, code):
        self.ip = 0
        self.stack = []
        self.loop_stack = []
        # code is just whitespace separated so we can use split() to read it
        self.tokens = code.split()
        while self.ip < len(self.tokens):
            self.evaluate_token(self.tokens[self.ip])
            self.ip += 1
        print()

p = Pforf()
if __name__ == "__main__":
    interpreter = Pforf()

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r') as file:
                code = file.read()
                interpreter.run(code)
        except FileNotFoundError:
            print(f"Error: The file '{filepath}' was not found.")
    else:
        print("Usage: python pforf.py <filename.pf>")
