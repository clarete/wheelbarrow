#!/usr/bin/env python3
import enum
from pprint import pprint

VALID_ATOM_CHARS = ('_', '-', '+', '*', '/', '>', '<')


class TokenType(enum.Enum):
    (OPEN_PAR,
     CLOSE_PAR,
     ATOM,
     INTEGER,
     STRING,
     DOT,
    ) = range(6)


class Token:
    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
    def __repr__(self):
        return "Token({}, {})".format(self._type, repr(self.value))
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other._type == self._type and
                other.value == self.value)


class Atom:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "Atom({})".format(repr(self.name))
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.name == self.name)


class Nil:
    def __repr__(self):
        return 'Nil'
    def __eq__(self, other):
        return isinstance(other, self.__class__)


nil = Nil()


def tokenize(code):
    i = 0
    c = lambda n=0: (i+n) < len(code) and code[i+n] or None
    while True:
        if c() is None: break
        elif c() == '(': yield Token(TokenType.OPEN_PAR)
        elif c() == ')': yield Token(TokenType.CLOSE_PAR)
        elif c().isdigit() or (c() == '-' and c(1) and c(1).isdigit()):
            d = i
            if c() == '-': i += 1
            while c() and c().isdigit(): i += 1
            yield Token(TokenType.INTEGER, int(code[d:i]))
            continue
        elif c() == '"':
            i += 1; d = i;
            while c() and c() != '"': i += 1
            yield Token(TokenType.STRING, code[d:i]); i += 1;
            continue
        elif c().isalpha() or c() in VALID_ATOM_CHARS:
            d = i
            while c() and (c().isalnum() or c() in VALID_ATOM_CHARS): i += 1
            yield Token(TokenType.ATOM, code[d:i])
            continue
        i += 1


class Parser:

    def __init__(self, code):
        self.code = code
        self.token = None
        self.tokens = tokenize(self.code) # Lazy

    def nextToken(self):
        try: self.token = next(self.tokens)
        except StopIteration: return None

    def testToken(self, _type):
        return self.token._type == _type

    def matchToken(self, _type):
        if not self.testToken(_type): return False
        self.nextToken()
        return True

    def returnCurrentAndMoveNext(self):
        # This quietly converts atoms to Atom instances
        value = (self.testToken(TokenType.ATOM)
                 and Atom(self.token.value)
                 or self.token.value)
        self.nextToken()
        return value

    def parseCons(self):
        if self.matchToken(TokenType.CLOSE_PAR): return None
        a = self.parseValue()
        if not a: return None

        if self.matchToken(TokenType.DOT):
            b = self.parseValue()
            if b: return [a, b]
            else: return [a, nil]

        b = self.parseCons()
        if b: return [a, b]
        else: return [a, nil]

    def parseValue(self):
        if self.matchToken(TokenType.OPEN_PAR):
            return self.parseCons()
        elif self.testToken(TokenType.INTEGER):
            return self.returnCurrentAndMoveNext()
        elif self.testToken(TokenType.ATOM):
            return self.returnCurrentAndMoveNext()
        elif self.testToken(TokenType.STRING):
            return self.returnCurrentAndMoveNext()
        return None

    def parse(self):
        self.nextToken()
        return self.parseValue()


def parse(tokens):
    return Parser(tokens).parse()


def car(l): return l[0]


def cdr(l): return l[1]


def primSum(args, env):
    tmp = args; total = 0
    while tmp != nil:
        total += tmp[0]
        tmp = tmp[1]
    return total


def evalList(v, env):
    if isinstance(v, Nil): return nil
    return [evalValue(car(v), env), evalList(cdr(v), env)]


def applyCons(v, env):
    f = evalValue(car(v), env)
    args = evalList(cdr(v), env)
    return f(args, env)


def evalValue(v, env):
    if isinstance(v, int): return v
    elif isinstance(v, str): return v
    elif isinstance(v, Atom): return env[v.name]
    elif isinstance(v, list): return applyCons(v, env)


def evaluate(code):
    return evalValue(Parser(code).parse(), {
        '+': primSum
    })


def main():
    pass


def test_tokenizer():
    run = lambda c: list(tokenize(c))

    assert(run('1')                          == [Token(TokenType.INTEGER, 1)])

    assert(run('-1')                         == [Token(TokenType.INTEGER, -1)])

    assert(run('test')                       == [Token(TokenType.ATOM, 'test')])

    assert(run('"test"')                     == [Token(TokenType.STRING, 'test')])

    assert(run('()')                         == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.CLOSE_PAR, None)])

    assert(run('(a b c)')                    == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.ATOM, 'b'),
                                                 Token(TokenType.ATOM, 'c'),
                                                 Token(TokenType.CLOSE_PAR, None)])

    assert(run('(first (+ 2 3))')            == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'first'),
                                                 Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, '+'),
                                                 Token(TokenType.INTEGER, 2),
                                                 Token(TokenType.INTEGER, 3),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.CLOSE_PAR, None)])

    assert(run('(first (list 1 (+ 2 3) 9))') == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'first'),
                                                 Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'list'),
                                                 Token(TokenType.INTEGER, 1),
                                                 Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, '+'),
                                                 Token(TokenType.INTEGER, 2),
                                                 Token(TokenType.INTEGER, 3),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.INTEGER, 9),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.CLOSE_PAR, None)])


def test_parser():
    run = lambda c: parse(c)

    # pprint(run('1'))
    assert(run('1')                          == 1)

    # pprint(run('"test"'))
    assert(run('"test"')                     == 'test')

    # pprint(run('atom'))
    assert(run('atom')                       == Atom('atom'))

    # pprint(run('(a)'))
    assert(run('(a)')                        == [Atom('a'), nil])

    # pprint(run('(+ 2 (* 3 5))'))
    assert(run('(+ 2 (* 3 5))')              == [Atom('+'), [2, [[Atom('*'), [3, [5, nil]]], nil]]])

    # pprint(run('(+ 2 (* 3 5) (* -1))'))
    assert(run('(+ 2 (* 3 5) (* -1))')       == [Atom('+'), [2, [[Atom('*'), [3, [5, nil]]],
                                                                 [[Atom('*'), [-1, nil]], nil]]]])

    # pprint(run('(first (list 1 (+ 2 3) 9))'))
    assert(run('(first (list 1 (+ 2 3) 9))') == [Atom('first'), [[Atom('list'),
                                                            [1, [[Atom('+'), [2, [3, nil]]],
                                                                 [9, nil]]]], nil]])


def test_evaluator():
    run = lambda c: evaluate(c)

    # pprint(run('1'))
    assert(run('1')                          == 1)

    # pprint(run('"test"'))
    assert(run('"test"')                     == 'test')

    # TODO: Error handling
    # pprint(run('atom'))
    # assert(run('atom')                       == Atom('atom'))

    # pprint(run('(+ 3 2)'))
    assert(run('(+ 3 2)')                      == 5)


def test():
    test_tokenizer()
    test_parser()
    test_evaluator()


if __name__ == '__main__':
    test()
