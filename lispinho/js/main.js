// lispinho.js
//
// Copyright (C) 2018  Lincoln Clarete
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

const readline = require('readline');

const TokenTypes = {
  OpenPar:  0,
  ClosePar: 1,
  Integer:  2,
  Atom:     3,
};

class Atom {
  constructor(name) {
    this.name = name;
  }
}

function tokenize(input) {
  let i = 0;
  const curr = (n=0) => i + n < input.length ? input[i] : null;
  const test = (re) => curr() && curr().match(re);
  const match = (re) => {
    if (test(re)) {
      i++;
      return true;
    }
    return false;
  };
  return (() => {
    while (curr() && curr().match(/\s/)) i++;
    if (curr() == null) return null;
    else if (match(/\(/)) return { type: TokenTypes.OpenPar };
    else if (match(/\)/)) return { type: TokenTypes.ClosePar };
    else if (test(/\d/)) {
      const d = i; while (test(/\d/)) i++;
      return { type: TokenTypes.Integer, value: parseInt(input.slice(d, i), 10) };
    }
    else if (test(/[a-zA-Z\+\-\*\/]/)) {
      const d = i; while (test(/[\w\+\-\*\/]/)) i++;
      return { type: TokenTypes.Atom, value: input.slice(d, i) };
    }
    else throw new Error(`Char ${curr()} not expected`);
  });
}

function parse(input) {
  const t = tokenize(input);
  let tok = t();
  const curr = () => tok;
  const test = (t) => tok && tok.type === t;
  const next = () => tok = t();
  const match = (t) => {
    if (test(t)) {
      next();
      return true;
    }
    return false;
  };
  const rnext = () => {
    const value = tok.value;
    next();
    return value;
  };
  const list = () => {
    if (match(TokenTypes.ClosePar)) return null;
    return [value(), list()];
  };
  const value = () => {
    if (!tok) return null;
    else if (match(TokenTypes.OpenPar)) return list();
    else if (test(TokenTypes.Integer)) return rnext();
    else if (test(TokenTypes.Atom)) return new Atom(rnext());
    throw new Error(`Unknown token ${JSON.stringify(tok)}`);
  };
  return value;
}

const car = (l) => l[0];
const cdr = (l) => l[1];

function evaluate(input) {
  const p = parse(input);
  const evalCons = (e, c) => {
    const f = value(e, car(c));
    if (f instanceof Function) return f(e, cdr(c));
    throw new Error(`Object ${f} is not callable`);
  };
  const value = (e, v) => {
    if (!v) return null;
    else if (typeof v === 'number') return v;
    else if (v instanceof Atom) return e[v.name];
    else if (Array.isArray(v)) return evalCons(e, v);
    throw new Error(`Unknown thing ${v} ${typeof v}`);
  };

  const primSum = (env, args) => {
    if (args === null) return 0;
    return value(env, car(args)) + primSum(env, cdr(args));
  };
  const primDefine = (env, args) => {
    env[car(args).name] = value(env, car(cdr(args)));
  };
  const env = {
    '+': primSum,
    'define': primDefine,
  };
  return () => {
    let last, expr = p();
    while (expr) {
      last = value(env, expr);
      expr = p();
    }
    return last;
  };
}

// ---- Test tools ----

function assert(expr, msg) {
  if (!expr) throw new Error(msg);
}

function assertEq(a, b, msg) {
  // console.log(JSON.stringify(a), JSON.stringify(b));
  assert(JSON.stringify(a) === JSON.stringify(b), msg);
}

// ---- Tests ----

function testTokenizer() {
  assertEq(tokenize('1')(), { type: TokenTypes.Integer, value: 1 }, "Can't tokenize integer");
  assertEq(tokenize('an-atom')(), { type: TokenTypes.Atom, value: 'an-atom' }, "Can't tokenize atom");

  const t0 = tokenize('(22 23 24)');
  assertEq(t0(), { type: TokenTypes.OpenPar }, "Should be OpenPar");
  assertEq(t0(), { type: TokenTypes.Integer, value: 22 }, "Should be 22");
  assertEq(t0(), { type: TokenTypes.Integer, value: 23 }, "Should be 23");
  assertEq(t0(), { type: TokenTypes.Integer, value: 24 }, "Should be 24");
  assertEq(t0(), { type: TokenTypes.ClosePar }, "Should be ClosePar");

  const t1 = tokenize('(+ 2 (* 3 4))');
  assertEq(t1(), { type: TokenTypes.OpenPar }, "Should be OpenPar");
  assertEq(t1(), { type: TokenTypes.Atom, value: '+' }, "Should be +");
  assertEq(t1(), { type: TokenTypes.Integer, value: 2 }, "Should be 2");
  assertEq(t1(), { type: TokenTypes.OpenPar }, "Should be OpenPar");
  assertEq(t1(), { type: TokenTypes.Atom, value: '*' }, "Should be *");
  assertEq(t1(), { type: TokenTypes.Integer, value: 3 }, "Should be 3");
  assertEq(t1(), { type: TokenTypes.Integer, value: 4 }, "Should be 4");
  assertEq(t1(), { type: TokenTypes.ClosePar }, "Should be ClosePar");
  assertEq(t1(), { type: TokenTypes.ClosePar }, "Should be ClosePar");
}

function testParse() {
  const p0 = parse('1');
  assertEq(p0(), 1, "Can't parse integer");

  const p1 = parse('an-atom');
  assertEq(p1(), new Atom('an-atom'), "Can't parse atom");

  const p2 = parse('(1 2 3)');
  assertEq(p2(), [1, [2, [3, null]]], "Can't parse list");

  const p3 = parse('(+ 1 (* 2 3) 4)');
  assertEq(p3(), [new Atom('+'), [1, [[new Atom('*'), [2, [3, null]]], [4, null]]]], "Can't parse sub list");
}

function testEvaluate() {
  const e0 = evaluate('1');
  assertEq(e0(), 1, "Can't eval integer");

  const e1 = evaluate('myatom');
  assertEq(e1(), undefined, "Can't eval atom in env");

  const e2 = evaluate('(+ 2 3)');
  assertEq(e2(), 5, "Can't eval sum");

  const e3 = evaluate('(define foo 3) (+ foo 4)');
  assertEq(e3(), 7, "Can't eval define and sum");
}

function repl() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  const setPrompt = () => {
    const prefix = '> ';
    rl.setPrompt(prefix, prefix.length);
    rl.prompt();
  };

  rl.on('line', (line) => {
    console.log(evaluate(line)());
    setPrompt();
  });

  setPrompt();
}

function main() {
  testTokenizer();
  testParse();
  testEvaluate();
  repl();
}

if (!module.parent) main();
