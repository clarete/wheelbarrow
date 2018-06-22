#!/usr/bin/env python3
# Licensed under GPLv3: https://www.gnu.org/licenses/gpl.txt
# Commit history available here: https://github.com/clarete/wheelbarrow/blob/master/lispinho/main.py
# no dependencies, may also work with python2
from __future__ import print_function
from pprint import pprint

import enum
import readline
import sys

# Python 2 portability
try: input = raw_input
except NameError: pass

__version__ = '0.0.1'

VALID_ATOM_CHARS = ('_', '-', '+', '*', '/', '>', '<')


class TokenType(enum.Enum):
    (OPEN_PAR,
     CLOSE_PAR,
     QUOTE,
     ATOM,
     INTEGER,
     FLOAT,
     STRING,
     DOT,
     QUASIQUOTE,
     UNQUOTE,
     SPLICE,
     END,
    ) = range(12)


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
    def callBody(self, argEnv):
        if isinstance(self.body, Nil): return nil
        return car(_flattenCons(self.body, argEnv))
    def __call__(self, args, env):
        assert(len(self.arglist) == len(args))
        argEnv = env.copy()
        # No parameters, let's bail
        if isinstance(self.arglist, Nil):
            return self.callBody(argEnv)
        i, head, tail = 0, car(self.arglist), cdr(self.arglist)
        flattenArgs = _flattenCons(args, env)
        while head != nil:
            assert(isinstance(head, Atom))
            argEnv[head.name] = flattenArgs[i]
            i += 1
            if tail == nil: break
            head, tail = car(tail), cdr(tail)
        return self.callBody(argEnv)


class Nil:
    def __repr__(self):
        return 'nil'
    def __eq__(self, other):
        return isinstance(other, self.__class__)
    def __len__(self):
        return 0


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
        elif c() == '`': yield Token(TokenType.QUASIQUOTE)
        elif c() == ',' and c(1) and c(1) == '@':
            yield Token(TokenType.SPLICE); i += 1
        elif c() == ',': yield Token(TokenType.UNQUOTE)
        elif c().isdigit() or (c() == '-' and c(1) and c(1).isdigit()):
            d = i
            if c() == '-': i += 1
            _type = TokenType.INTEGER
            while c() and (c().isdigit() or c() == '.'):
                if c() == '.': _type = TokenType.FLOAT
                i += 1
            yield Token(_type, (int(code[d:i])
                                if _type == TokenType.INTEGER
                                else float(code[d:i])))
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
        self.nextToken()

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
        if a is None: return None

        if self.matchToken(TokenType.DOT):
            b = self.parseValue()
            if b: return [a, b]
            else: return [a, nil]

        b = self.parseCons()
        if b is not None: return [a, b]
        else: return [a, nil]

    def parseValue(self):
        if self.matchToken(TokenType.OPEN_PAR):
            return self.parseCons()
        if self.matchToken(TokenType.QUOTE):
            return wrapFn('quote', self.parseValue())
        elif self.matchToken(TokenType.QUASIQUOTE):
            return wrapFn('quasiquote', self.parseValue())
        elif self.matchToken(TokenType.UNQUOTE):
            return wrapFn('unquote', self.parseValue())
        elif self.matchToken(TokenType.SPLICE):
            return wrapFn('splice', self.parseValue())
        elif self.testToken(TokenType.INTEGER):
            return self.returnCurrentAndMoveNext()
        elif self.testToken(TokenType.FLOAT):
            return self.returnCurrentAndMoveNext()
        elif self.testToken(TokenType.ATOM):
            return self.returnCurrentAndMoveNext()
        elif self.testToken(TokenType.STRING):
            return self.returnCurrentAndMoveNext()
        return None

    def parse(self):
        return self.parseValue()


def parse(tokens):
    return Parser(tokens).parse()


def isFn(v, name): return isinstance(v, Atom) and v.name == name

def wrapFn(fn, v): return [Atom(fn), [v, nil]]

def car(l): return l[0]

def caar(l): return car(l[0])

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
    if isinstance(args, Nil): return Lambda(nil, nil)
    return Lambda(car(args), cdr(args))


def primPrint(args, env):
    printobj(evalValue(car(args), env))


def primEval(args, env):
    return evaluate(car(args), env)


def evalCons(v, env):
    f = evalValue(car(v), env)
    assert(callable(f))
    return f(cdr(v), env)


def lookup(env, name):
    try: return env[name]
    except KeyError: pass
    raise NameError('Atom `{}\' is not defined'.format(name))


def evalValue(v, env):
    if isinstance(v, (int, float, str)): return v
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
    parser = Parser(code)
    lastValue = None
    while True:
        expr = parser.parse()
        if expr is None: break
        lastValue = evalValue(expr, env)
    return lastValue


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

    assert(run('3.141592653589793')          == [Token(TokenType.FLOAT, 3.141592653589793),
                                                 Token(TokenType.END, None)])

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

    assert(run("(1.2 3.4)")                  == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.FLOAT, 1.2),
                                                 Token(TokenType.FLOAT, 3.4),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    # pprint(run('(print 0)'))
    assert(run('(print 0)')                  == [Token(TokenType.OPEN_PAR, None),
                                                 Token(TokenType.ATOM, 'print'),
                                                 Token(TokenType.INTEGER, 0),
                                                 Token(TokenType.CLOSE_PAR, None),
                                                 Token(TokenType.END, None)])

    # pprint(run("`'a"))
    assert(run("`'a")                        == [Token(TokenType.QUASIQUOTE),
                                                 Token(TokenType.QUOTE),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.END)])


    # pprint(run("`(a ,@(list 1 2) c)"))
    assert(run("`(a ,@(list 1 2) c)")        == [Token(TokenType.QUASIQUOTE),
                                                 Token(TokenType.OPEN_PAR),
                                                 Token(TokenType.ATOM, 'a'),
                                                 Token(TokenType.SPLICE),
                                                 Token(TokenType.OPEN_PAR),
                                                 Token(TokenType.ATOM, 'list'),
                                                 Token(TokenType.INTEGER, 1),
                                                 Token(TokenType.INTEGER, 2),
                                                 Token(TokenType.CLOSE_PAR),
                                                 Token(TokenType.ATOM, 'c'),
                                                 Token(TokenType.CLOSE_PAR),
                                                 Token(TokenType.END)])


def test_parser():
    run = lambda c: parse(c)

    # pprint(run('1'))
    assert(run('1')                          == 1)

    # pprint(run('3.141592653589793'))
    assert(run('3.141592653589793')          == 3.141592653589793)

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

    # pprint(run("'test"))
    assert(run("'test")                      == [Atom('quote'), [Atom('test'), nil]])

    # pprint(run('(1.2 3.4)'))
    assert(run('(1.2 3.4)')                  == [1.2, [3.4, nil]])

    # pprint(run('(print 0)'))
    assert(run('(print 0)')                  == [Atom('print'), [0, nil]])

    # pprint(run("`'a"))
    assert(run("`'a")                        == [Atom('quasiquote'),
                                                 [[Atom('quote'), [Atom('a'), nil]],
                                                  nil]])

    # pprint(run("`(a ,@'(1 2) c)"))
    assert(run("`(a ,@'(1 2) c)")            == [Atom('quasiquote'),
                                                 [[Atom('a'),
                                                   [[Atom('splice'), [[Atom('quote'), [[1, [2, nil]], nil]], nil]],
                                                    [Atom('c'), nil]]],
                                                  nil]])


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

    # pprint(run("'a"))
    assert(run("'an-atom")                   == Atom('an-atom'))

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

    # pprint(run("(+ 1.2 3.4)"))
    assert(run("(+ 1.2 3.4)") == 4.6)

    # pprint(run("((lambda (x) (+ x 1)) 2)"))
    assert(run("((lambda (x) (+ x 1)) 2)") == 3)

    # pprint(run("((lambda ()))"))
    assert(run("((lambda ()))") == nil)


def test():
    test_tokenizer()
    test_parser()
    test_evaluator()


if __name__ == '__main__':
    test()
    main()
