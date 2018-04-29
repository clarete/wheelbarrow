const eg_template = "To understand $x you must first understand @y.";

const eg_env = {
  x: 'recursion',
  y: ['base cases', 'recursion'],
};

/** #1. Interpreted version. Analyzing the template & producing output
        happen in the same pass. */
function fill(t, env) {
  if      (t === '')     return '';
  else if (t[0] === '$') return env[t[1]]               + fill(t.slice(2), env);
  else if (t[0] === '@') return env[t[1]].join(' and ') + fill(t.slice(2), env);
  else                   return t[0]                    + fill(t.slice(1), env);
}
console.log(fill(eg_template, eg_env));

/** #2. First compiled version. Template analyzer returns chain of
        closures that get executed with data for each output
        generator. */
function makeFiller(t) {
  if      (t === '')     return (env) => '';
  else if (t[0] === '$') return (env) => env[t[1]]               + fill(t.slice(2), env);
  else if (t[0] === '@') return (env) => env[t[1]].join(' and ') + fill(t.slice(2), env);
  else                   return (env) => t[0]                    + fill(t.slice(1), env);
}
console.log(makeFiller(eg_template)(eg_env));

/** #3. Another compiled version. Template analyzer walks the template
        and builds appropriate objects recursively and the output
        generation is delegated to these objects. */
const Empty    = () => '';
const Hole     = (name, rest) => (env) => env[name]               + rest(env);
const ListHole = (name, rest) => (env) => env[name].join(' and ') + rest(env);
const Constant = (name, rest) => (env) => name                    + rest(env);
function makeFiller2(t) {
  if      (t === '')     return Empty;
  else if (t[0] === '$') return Hole    (t[1], makeFiller2(t.slice(2)));
  else if (t[0] === '@') return ListHole(t[1], makeFiller2(t.slice(2)));
  else                   return Constant(t[0], makeFiller2(t.slice(1)));
}
console.log(makeFiller2(eg_template)(eg_env));
