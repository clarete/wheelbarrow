// lispinho.js - tiny lisp
//
// Copyright (C) 2019  Lincoln Clarete
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
const fs = require('fs');

const err = (msg) => { throw new Error(msg); };
class Lambda { constructor(a,b) { this.args = a; this.body = b; } }

function parse(source) {
  // Lexer
  let cursor = 0;
  const currc = () => source[cursor] || '';
  const nextc = () => source[cursor++];
  const match = (c) => currc() === c ? nextc() : false;
  const must = (c) => { if (!match(c)) throw new Error(`Missing '${c}'`); };
  // Is the cursor at a number
  const isAtNum = () => /[\d.]+/.test(currc());
  // Is the cursor at an identifier
  const isIdentStart = () => /[A-Za-z%<>=+*\/\-_]/.test(currc());
  const isIdentCont = () => /[A-Za-z0-9%<>=*+\/\-_]/.test(currc());
  // Is it the true constant
  const isTrueStart = () => currc() === '#';
  const isTrueCont = () => ['#', 't'].includes(currc());
  // Comments
  const isCommentStart = () => currc() === ';';
  const isCommentCont = () => currc() !== '\n';
  // Collect prefix that matches a prediate
  const consume = (predicate) => {
    let chars = "";
    while (predicate()) chars += nextc();
    return chars;
  };
  const space = () => consume(() => [' ', '\r', '\n', '\t'].includes(currc()));
  const comments = () => isCommentStart() ? consume(isCommentCont) : '';
  const s = () => { space(); comments(); space(); };
  const parseNumber = () => parseFloat(consume(isAtNum));
  const parseSymbol = () => Symbol.for(consume(isIdentCont));
  const parseTrue = () => consume(isTrueCont) && true;
  const parseList = () => {
    const items = [];
    while (true) {
      const value = parseValue(); s();
      if (value !== null) items.push(value);
      else break;
    }
    must(")"); s();
    return items;
  };
  const parseValue = () => {
    s(); if (match("(")) return parseList();
    else if (isAtNum()) return parseNumber();
    else if (isTrueStart()) return parseTrue();
    else if (isIdentStart()) return parseSymbol();
    else return null;
  };
  // Handle multiple lists in the same stream;
  const lists = [];
  while (true) {
    const v = parseValue();
    if (v !== null) lists.push(v);
    else break;
  }
  switch (lists.length) {
  case 0: return err(`No entiendo [${cursor}]`);
  case 1: return lists.pop();
  default: return [Symbol.for('progn'), ...lists];
  }
}

function applyLambda(lambda, argVals, env) {
  if (argVals.length !== lambda.args.length)
    err(`Expected ${lambda.args.length} params, ` +
        `received ${argVals.length}`);
  const envFromArgs = lambda.args.reduce((obj, x) => {
    obj[x] = evaluate(argVals.shift(), env);
    return obj;
  }, {});
  return evaluate(lambda.body, { ...env, ...envFromArgs });
}

function apply(list, env) {
  const c = evaluate(list.shift(0), env);
  if (c instanceof Lambda) return applyLambda(c, list, env);
  else return c.apply(null, [env].concat(list));
  return null;
}

function evaluate(tree, env) {
  switch (typeof tree) {
  case 'boolean':               // fallthrough
  case 'number': return tree;
  case 'object': return apply(tree.slice(), env);
  case 'symbol': return env.hasOwnProperty(tree)
      ? env[tree]
      : err(`${tree.toString()} not defined`);
  default: return err(`${typeof tree} who?`);
  }
}

function defaultEnv() {
  const s = Symbol.for;
  const ev = evaluate;
  return {
    [s('nil')]: null,
    // Arithmetic
    [s('+')]: (e,...a) => a.reduce((x,y) => ev(x,e) + ev(y,e), 0),
    [s('-')]: (e,...a) => a.reduce((x,y) => ev(x,e) - ev(y,e), 0),
    [s('/')]: (e,a,b) => ev(a,e) / ev(b,e),
    [s('*')]: (e,a,b) => ev(a,e) * ev(b,e),
    [s('**')]: (e,a,b) => ev(a,e) ** ev(b,e),
    [s('%')]: (e,a,b) => ev(a,e) % ev(b,e),
    // Comparison
    [s('>')]: (e,a,b) => ev(a,e) > ev(b,e),
    [s('<')]: (e,a,b) => ev(a,e) < ev(b,e),
    [s('>=')]: (e,a,b) => ev(a,e) >= ev(b,e),
    [s('<=')]: (e,a,b) => ev(a,e) <= ev(b,e),
    [s('=')]: (e,a,b) => ev(a,e) === ev(b,e),
    // Lisp
    [s('print')]: (e,thing) => console.log(ev(thing,e)),
    [s('quote')]: (e,thing) => thing,
    [s('define')]: (e,n,v) => e[n] = ev(v,e),
    [s('lambda')]: (e,a,b) => new Lambda(a, b),
    [s('progn')]: (e,...ls) => ls.map(l => ev(l,e))[ls.length-1],
    [s('if')]: (e,c,t,f) => ev(c,e) ? ev(t,e) : f ? ev(f,e) : null,
    [s('car')]: (e,c) => ev(c,e)[0],
    [s('cdr')]: (e,c) => ev(c,e).slice(1),
    [s('len')]: (e,c) => ev(c,e).length,
  };
}

// ---- Test tools ----

function assert(expr, msg) { if (!expr) throw new Error(msg); }
function assertEq(a, b, msg) {
  if (typeof a !== typeof b) throw new Error(msg);
  if (typeof a === Symbol || typeof b === Symbol) return a === b;
  return assert(JSON.stringify(a) === JSON.stringify(b), msg);
}

// ---- Tests ----

function testParse() {
  // Numbers
  const p0 = parse('1');
  assertEq(p0, 1, "Can't parse integer");
  // Booleans
  const p1 = parse('#t');
  assertEq(p1, true, "Can't parse true");
  // Atom
  const p2 = parse('an-atom');
  assertEq(p2, Symbol('an-atom'), "Can't parse atom");
  // Lists
  const p3 = parse('(1 2 3)');
  assertEq(p3, [1, 2, 3], "Can't parse list");
  // Lists of lists
  const p4 = parse('(+ 1 (* 2 3) 4)');
  assertEq(p4, [Symbol.for('+'), 1, [Symbol.for('*'), 2, 3], 4], "Can't parse sub list");
  // Consecutive lists
  const p5 = parse('(+ 1) (/ 2)');
  assertEq(p5, [Symbol.for('progn'), [Symbol.for('+'), 1], [Symbol.for('/'), 2]],
           "Can't parse consecutive lists");
  // Lambdas
  const p6 = parse('(lambda (a) (+ a 4))');
  assertEq(p6, [Symbol.for('lambda'), [Symbol.for('a')], [Symbol.for('+'), Symbol.for('a'), 4]],
           "Can't parse lambda");
}

function testEvaluate() {
  // Test eval Number 1
  assertEq(evaluate(parse('1'), {}), 1, "Can't eval integer");
  assertEq(evaluate(parse('0'), {}), 0, "Can't eval integer");
  // Test eval True
  assertEq(evaluate(parse('#t'), {}), true, "Can't eval true");
  // Test can't find symbol
  let passed_e1 = false;
  try { evaluate(parse('myatom'), {}); }
  catch (err) {
    passed_e1 = true;
    assertEq(err, new Error("Symbol(myatom) not defined"), "Can't eval atom in env");
  } assert(passed_e1, "Didn't throw");
  // Test can find symbol
  const e1_1 = evaluate(parse('oi'), {[Symbol.for('oi')]: 1});
  assertEq(e1_1, 1, "Can't eval atom oi in env");
  // Test execute primitive functions
  const e2 = evaluate(parse('(+ 2 3)'), defaultEnv());
  assertEq(e2, 5, "Can't eval sum");
  // Test define variable
  const e3 = evaluate(
    parse('(define foo 3) (+ foo 4)'),
    defaultEnv());
  assertEq(e3, 7, "Can't eval define and sum");
  // Test Evaluate Lambdas
  const e4 = evaluate(parse('((lambda (a) (+ a 4)) 1)'), defaultEnv());
  assertEq(e4, 5, "Can't eval lambda");
  // Test If
  assertEq(evaluate(parse('(if #t 1 2)'), defaultEnv()), 1, "Can't eval if expr");
  assertEq(evaluate(parse('(if nil 1 2)'), defaultEnv()), 2, "Can't eval if/else expr");
  assertEq(evaluate(parse('(if nil 1)'), defaultEnv()), null, "Can't eval if without else expr");
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

  const env = defaultEnv();

  rl.on('line', (line) => {
    if (line.trim() !== '') {
      const p = parse(line);
      const v = evaluate(p, env);
      if (v !== undefined) console.log(v);
    }
    setPrompt();
  });

  setPrompt();
}

function file() {
  const content = fs.readFileSync(process.argv[2]).toString();
  evaluate(parse(content), defaultEnv());
}
function run() { process.argv.length === 3 ? file() : repl(); }
function main() { testParse(); testEvaluate(); run(); }
module.exports = { parse, evaluate };
if (!module.parent) main();
