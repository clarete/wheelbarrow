eg_template = "To understand $x you must first understand @y."

eg_env = {
    'x': 'recursion',
    'y': ['base cases', 'recursion'],
}

### Purely interpreted version

def fill(t, env):
    if   t    == '':  return ''
    elif t[0] == '$': return env[t[1]]               + fill(t[2:], env)
    elif t[0] == '@': return ' and '.join(env[t[1]]) + fill(t[2:], env)
    else:             return t[0]                    + fill(t[1:], env)
print(fill(eg_template, eg_env))

### Compiled into functions

def make_filler(t):
    if   t    == '':  return lambda env: ''
    elif t[0] == '$': return lambda env: env[t[1]]                + make_filler(t[2:])(env)
    elif t[0] == '@': return lambda env: ' and '.join(env[t[1]])  + make_filler(t[2:])(env)
    else:             return lambda env: t[0]                     + make_filler(t[1:])(env)
print(make_filler(eg_template)(eg_env))
