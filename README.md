# State Machine Exercise

## Task

1. Develop a framework for implementing state machines
2. Solve a problem using the framework
3. Implement persistence feature

## Framework

A state machine is quite a general name, but it usually references
finite state machines, so I'll limit myself to this subclass only,
not considering infinite number of states.

There is further classification of finite state machines:

- Acceptors
- Classifiers
- Transducers
- Sequencers

The difference can be vaguely described as the cardinality of output
and the presence of actions on states or transitions. From this list,
acceptors (also called finite automata) and transducers are implemented.

The framework is presented as a library `fsmlib`, which includes (as of
now) a single module `automata` with submodules `state`, `acceptors` and
`transducers`, which should be self-explanatory in the contents. The
`state` submodule is an attempt at unifying the shared concepts between
different machines. A similar attempt can be performed on deterministic
automata, but was not explored as of now.

To install:
```bash
python -m venv ./venv
source venv/bin/activate
pip install .
```

Example use with a DFA:

```python
from fsmlib.automata.acceptors import DFA
from fsmlib.automata.state import DFAState

# declare states
p = DFAState(name="p", initial=True, accepting=True)
q = DFAState(name="q")

# declare transitions
p.add_transition(0, q)
p.add_transition(1, p)
q.add_transition(0, p)
q.add_transition(1, q)

# declare the state machine
machine = DFA(initial=p, alphabet=[0, 1])

# review the ASCII graph of the machine
print(machine)

# test sequences with the machine
print(machine.accept([]))
print(machine.accept([1]))
print(machine.accept([0, 0]))
print(machine.accept([1, 0, 1]))
print(machine.accept([0, 0, 1]))
```

## Toy problem

> The production line is supposed to alternately output one Strawberry-flavored
> lollipop, then one Lemon-flavored one, then another one Strawberry-flavored
> lollipop, and so on and so forth. Now, in some cases, due to some fluke there
> can be a case where two lollipops of the same flavor appear one after the other,
> and that’s fine. However, if three lollipops of the same flavor appear in a row,
> that likely means there is some serious problem, and we need to call an Engineer
> to review the machines. Task is to build a state machine that will detect errors,
> every time an error happens but not treating consecutive output of the same
> flavor as another error.

A solution to the toy problem with the developed framework is presented in file
[`main.py`](main.py), which is runnable. The input is taken from command line as 
follows:
```bash
python main.py slsssssllll
```

## Persistence

Persistence is only implemented for Mealy Machine (to work with toy example) due
to time constraints. It is possible though and even easier to implement it with
other machines and in a unified way.

Persistence is implemented in the form of saving states and transitions as JSON
objects on disk:

```python
# define the machine and sequence
machine = MealyMachine(...)
sequence = ...

# process part of the sequence
for x in sequence[: len(sequence) // 2]:
    machine.forward(x)

# save the machine and its current state to disk
machine.save(Path("./machine.json"))

# remove machine from memory
del machine

# reinstantiate the machine from disk
machine = MealyMachine.load(Path("./machine.json"))

# continue processing from the saved state
for x in sequence[len(sequence) // 2 :]:
    machine.forward(x)
```