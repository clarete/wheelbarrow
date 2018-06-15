#!/usr/bin/env python3
# Licensed under GPLv3: https://www.gnu.org/licenses/gpl.txt
# Commit history available here: https://github.com/clarete/wheelbarrow/blob/master/lispinho/main.py
# no dependencies, may also work with python2
from __future__ import print_function
import enum
import readline
from pprint import pprint

VALID_ATOM_CHARS = ('_', '-', '+', '*', '/', '>', '<')


class TokenType(enum.Enum):
    (OPEN_PAR,
     CLOSE_PAR,
     QUOTE,
     ATOM,
     INTEGER,
     STRING,
     DOT,
     COLON,
     END,
    ) = range(9)


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
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.name == self.name)

class Lambda:
    def __init__(self, arglist, body):
        self.arglist = arglist
        self.body = body
    def __call__(self, args, env):
        assert(len(self.arglist) == len(args))
        argEnv = env.copy()
        i, head, tail = 0, car(self.arglist), cdr(self.arglist)
        flattenArgs = _flattenCons(args, env)
        while head != nil:
            assert(isinstance(head, Atom))
            argEnv[head.name] = flattenArgs[i]
            i += 1
            if tail == nil: break
            head, tail = car(tail), cdr(tail)
        return car(_flattenCons(self.body, argEnv))


class Nil:
    def __repr__(self):
        return 'nil'
    def __eq__(self, other):
        return isinstance(other, self.__class__)


nil = Nil()


def tokenize(code):
    i = 0
    c = lambda n=0: (i+n) < len(code) and code[i+n] or None
    while True:
        if c() is None: break
        elif c().isspace(): pass
        elif c() == '.': yield Token(TokenType.DOT)
        elif c() == '(': yield Token(TokenType.OPEN_PAR)
        elif c() == ')': yield Token(TokenType.CLOSE_PAR)
        elif c() == "'": yield Token(TokenType.QUOTE)
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
        elif c() == ';':
            while c() != '\n':
                i += 1
        else:
            raise SyntaxError("Unexpected char `{}'".format(c()))
        i += 1
    yield Token(TokenType.END)


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
        if self.matchToken(TokenType.QUOTE):
            return [Atom('quote'), [self.parseValue(), nil]]
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


def _flattenCons(v, env):
    if isinstance(v, Nil): return []
    out = [evalValue(car(v), env)]
    out.extend(_flattenCons(cdr(v), env))
    return out


def primSum(args, env):
    return sum(_flattenCons(args, env))


def primQuote(args, env):
    return car(args)


def primCond(args, env):
    head, tail = car(args), cdr(args)
    while head != nil:
        cond = evalValue(car(head), env)
        if cond != nil: return evalValue(car(cdr(head)), env)
        head, tail = car(tail), cdr(tail)
    return nil


def primLabel(args, env):
    assert(isinstance(car(args), Atom))
    value = evalValue(car(cdr(args)), env)
    env[car(args).name] = value
    return value


def primProgn(args, env):
    return _flattenCons(args, env)[-1]


def primLambda(args, env):
    return Lambda(car(args), cdr(args))


def primPrint(args, env):
    printobj(evalValue(car(args), env))


def primEval(args, env):
    return evaluate(car(args), env)


def evalCons(v, env):
    assert(isinstance(car(v), Atom))
    f = evalValue(car(v), env)
    return f(cdr(v), env)


def lookup(env, name):
    try: return env[name]
    except KeyError: pass
    raise NameError('Atom `{}\' is not defined'.format(name))


def evalValue(v, env):
    if isinstance(v, int): return v
    elif isinstance(v, str): return v
    elif isinstance(v, Atom): return lookup(env, v.name)
    elif isinstance(v, list): return evalCons(v, env)


primFuncs = {
    'nil': nil,
    '+': primSum,
    'quote': primQuote,
    'cond': primCond,
    'label': primLabel,
    'progn': primProgn,
    'lambda': primLambda,
    'print': primPrint,
    'eval': primEval,
}


def evaluate(code, env):
    return evalValue(Parser(code).parse(), env)


def printlist(l, end=' '):
    head, tail = car(l), cdr(l)
    print('(', end='')
    if not isinstance(tail, list):
        printobj(head, end='' if tail == nil else ' ')
        print('.', end=' ')
        return printobj(tail, end=')')
    while head != nil:
        printobj(head, end='' if tail == nil else ' ')
        if tail == nil: break
        head, tail = car(tail), cdr(tail)
    print(')', end=end)


def printobj(obj, end=''):
    if isinstance(obj, list): printlist(obj, end)
    else: print(obj, end=end)


def repl():
    env = primFuncs
    env.update({'exit': lambda args, env: exit()})
    print('lispinho {}'.format(__version__))
    print('Type (exit) and hit enter to go back to the terminal')
    while True:
        userInput = input("> ")
        if not userInput: continue
        value = evaluate(userInput, env)
        if value is not None: printobj(value)
        print()


def evalFile(fileName, env=primFuncs):
    return evaluate(open(fileName).read(), env)


def main(args=sys.argv[1:]):
    if args: return evalFile(args[0])
    try: repl()
    except EOFError: print()


def test_tokenizer():
    run = lambda c: list(tokenize(c))

    assert(run('1')                          == [Token(TokenType.INTEGER, 1), Token(TokenType.END, None)])

    assert(run('-1')                         == [Token(TokenType.INTEGER, -1), Token(TokenType.END, None)])

    assert(run('test')                       == [Token(TokenType.ATOM, 'test'), Token(TokenType.END, None)])

    assert(run('"test"')                     == [Token(TokenType.STRING, 'test'), Token(TokenType.END, None)])

    assert(run("'test")                      == [Token(TokenType.QUOTE, None),
                                                 Token(TokenType.ATOM, 'test'),
                                                 Token(TokenType.END, None)])

    assert(run('()')                         == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    assert(run('(a b c)')                    == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.ATOM, 'b'),
                                                 Token(TokenType.ATOM, 'c'),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    assert(run('(first (+ 2 3))')            == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'first'),
                                                 Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, '+'),
                                                 Token(TokenType.INTEGER, 2),
                                                 Token(TokenType.INTEGER, 3),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

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
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    assert(run('  (   a \n\n\n\r\n  b   ) ') == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.ATOM, 'b'),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    assert(run('(a . b)')                    == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.DOT, None),
                                                 Token(TokenType.ATOM, 'b'),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    assert(run('; foo\n1')                   == [Token(TokenType.INTEGER, 1),
                                                 Token(TokenType.END, None)])


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

    assert(run("'test")                      == [Atom('quote'), [Atom('test'), nil]])


def test_evaluator():
    run = lambda c: evaluate(c, primFuncs)

    # pprint(run('1'))
    assert(run('1')                          == 1)

    # pprint(run('"test"'))
    assert(run('"test"')                     == 'test')

    # TODO: Error handling
    # pprint(run('atom'))
    # assert(run('atom')                       == Atom('atom'))

    # pprint(run('(+ 3 2)'))
    assert(run('(+ 3 2)')                    == 5)

    # pprint(run('(quote a)'))
    assert(run('(quote a)')                  == Atom('a'))

    # pprint(run('(cond (nil 1) (nil 2) (1 3))'))
    assert(run('(cond (nil 1) (nil 2) (1 3))') == 3)

    # pprint(run('(label foo 1)'))
    assert(run('(label foo 1)') == 1)

    # pprint(run('(progn (label foo (lambda (x) (+ x 1)))'
    #            '       (foo 2))'))
    assert(run('(progn (label foo (lambda (x) (+ x 1)))'
               '       (foo 2))') == 3)

    # pprint(run('(progn (label foo (lambda (x y) (+ x y)))'
    #            '       (foo 2 3))'))
    assert(run('(progn (label foo (lambda (x y) (+ x y)))'
               '       (foo 2 3))') == 5)


def test():
    test_tokenizer()
    test_parser()
    test_evaluator()


if __name__ == '__main__':
    test()
    main()
