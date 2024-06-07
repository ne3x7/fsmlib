# State Machine Exercise

## Task

1. Develop a framework for implementing state machines
2. Solve a problem using the framework
3. Implement persistence feature

## Framework

A state machine is quite a general name, but it usually references
finite state machines, so I'll limit myself to this subclass only.

There is further classification of finite state machines:
- Acceptors
- Classifiers
- Transducers
- Sequencers

The difference can be vaguely described as the cardinality of output
and the presence of actions. Because acceptors are most common in
computer science, and for simplicity reasons, I will limit myself to
only acceptors FSM, also called finite automata.

The framework is presented as a library `fsmlib`, which includes the
following modules:
- `fsm` implements the classes for FSM
- 