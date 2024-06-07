from typing import Sequence, List, Set, Union, Any, Callable, Optional
from copy import deepcopy

from fsmlib.state import NFAState, DFAState, MooreState, MealyState


class NFA:
    initial: NFAState
    current: NFAState
    alphabet: List[Any]
    empty_char: Any

    def __init__(self, initial: NFAState, alphabet: List[Any], empty_char: Any) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet
        self.empty_char = empty_char
        if self.empty_char in self.alphabet:
            raise ValueError(f"Empty character must not be in alphabet.")

    def accept(self, sequence: Sequence) -> bool:
        return self._accept(sequence, self.initial)

    def _accept(self, sequence: Sequence, node: NFAState) -> bool:
        if len(sequence) == 0 and node.accepting:
            return True
        elif len(sequence) == 0:
            return False

        result = False

        target_states = node.transition(sequence[0])
        for state in target_states:
            result = result or self._accept(sequence[1:], state)

        target_states = node.transition(self.empty_char)
        for state in target_states:
            result = result or self._accept(sequence, state)

        return result

    def __repr__(self) -> str:
        return "\n".join(
            s for s in self._traverse_and_apply(
                node_fun=lambda s, h: "       " * h + s.name if s is not None else "",
                edge_fun=lambda s, t, c, h: "       " * h + f"  {c} -> {t.name}"
            ) if len(s) > 0
        )

    def _traverse_and_apply(
            self,
            node_fun: Callable[[Optional[NFAState], Optional[int]], Any],
            edge_fun: Callable[[NFAState, NFAState, Any, Optional[int]], Any]
    ) -> List[Any]:
        def helper(state: NFAState, visited: Set[str], hierarchy: int) -> Any:
            if state.name in visited:
                return [node_fun(None, 0)]

            visited.add(state.name)
            output = [node_fun(state, hierarchy)]
            for symbol, target_states in state.transitions.items():
                for target_state in target_states:
                    output.append(edge_fun(state, target_state, symbol, hierarchy))
                    output.extend(helper(target_state, visited, hierarchy + 1))

            return output

        return helper(self.initial, set(), 0)

    def to_dfa(self) -> "DFA":
        return nfa_to_dfa(self)


class DFA:
    initial: DFAState
    current: DFAState
    alphabet: List[Union[str, int]]

    def __init__(self, initial: DFAState, alphabet: List[Union[str, int]]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def process(self, x: Any) -> None:
        self.current = self.current.transition(x)

    def accept(self, sequence: Sequence) -> bool:
        return self._accept(sequence)

    def _accept(self, sequence: Sequence) -> bool:
        if len(sequence) == 0 and self.current.accepting:
            self.current = self.initial
            return True
        elif len(sequence) == 0:
            self.current = self.initial
            return False

        char = sequence[0]
        if char not in self.current.transitions:
            self.current = self.initial
            return False

        self.current = self.current.transitions[char]
        return self._accept(sequence[1:])

    @property
    def states(self) -> List[DFAState]:
        return list(self._traversal({self.initial}, self.initial))

    def _traversal(self, result: Set[DFAState], current: DFAState) -> Set[DFAState]:
        for name, node in current.transitions.items():
            if node not in result:
                result.add(node)
                node_traversal = self._traversal(result, node)
                result = result.union(node_traversal)
        return result

    @property
    def complete(self) -> bool:
        return all([
            len(set(self.alphabet).difference(state.transitions.keys())) == 0
            for state in self.states
        ])

    def __repr__(self) -> str:
        return "\n".join(
            s for s in self._traverse_and_apply(
                node_fun=lambda s, h: "       " * h + s.name if s is not None else "",
                edge_fun=lambda s, t, c, h: "       " * h + f"  {c} -> {t.name}"
            ) if len(s) > 0
        )

    def _traverse_and_apply(
        self,
        node_fun: Callable[[Optional[DFAState], Optional[int]], Any],
        edge_fun: Callable[[DFAState, DFAState, Any, Optional[int]], Any]
    ) -> List[Any]:
        def helper(state: DFAState, visited: Set[str], hierarchy: int) -> Any:
            if state.name in visited:
                return [node_fun(None, 0)]

            visited.add(state.name)
            output = [node_fun(state, hierarchy)]
            for symbol, target_state in state.transitions.items():
                output.append(edge_fun(state, target_state, symbol, hierarchy))
                output.extend(helper(target_state, visited, hierarchy + 1))

            return output

        return helper(self.initial, set(), 0)

    @classmethod
    def from_nfa(cls, nfa: NFA) -> "DFA":
        return nfa_to_dfa(nfa)


class MooreMachine:
    initial: MooreState
    current: MooreState
    alphabet: List[Any]

    def __init__(self, initial: MooreState, alphabet: List[Any]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def forward(self, x: Any) -> Any:
        self.current = self.current.transition(x)
        return self.current.output


class MealyMachine:
    initial: MealyState
    current: MealyState
    alphabet: List[Any]

    def __init__(self, initial: MealyState, alphabet: List[Any]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def forward(self, x: Any) -> Any:
        self.current, output = self.current.transition(x)
        return output


def nfa_eclosure(nfa: NFA, sub: Set[NFAState]) -> Set[NFAState]:
    states = set()
    states.update(sub)
    for state in sub:
        for target_state in state.transitions[nfa.empty_char]:
            states.add(target_state)
            states.update(nfa_eclosure(nfa, {target_state}))
    return states


def nfa_move(sub: Set[NFAState], char: str) -> Set[NFAState]:
    states = set()
    for state in sub:
        for target_state in state.transitions[char]:
            states.add(target_state)
    return states


def nfa_to_dfa(nfa: NFA) -> DFA:
    unmarked = []  # here live NFA+DFA states
    new_states = dict()  # here live DFA states

    q0 = nfa_eclosure(nfa, {nfa.initial})
    dfa_q0 = DFAState(
        name="+".join(sorted(state.name for state in q0)),
        initial=True,
        accepting=any([state.accepting for state in q0]),
        transitions={},
    )
    new_states[dfa_q0.name] = dfa_q0
    unmarked.append((q0, dfa_q0))

    has_unmarked = len(unmarked) > 0
    while has_unmarked:
        nfa_states, dfa_state = unmarked.pop()
        for symbol in nfa.alphabet:
            q = nfa_eclosure(nfa, nfa_move(nfa_states, symbol))
            if len(q) > 0:
                name = "+".join(sorted(state.name for state in q))
                if name not in new_states:
                    dfa_q = DFAState(
                        name=name,
                        initial=False,
                        accepting=any([state.accepting for state in q]),
                        transitions={},
                    )
                    new_states[dfa_q.name] = dfa_q
                    unmarked.append((q, dfa_q))
                else:
                    dfa_q = new_states[name]
                dfa_state.transitions[symbol] = dfa_q
        has_unmarked = len(unmarked) > 0

    return DFA(initial=dfa_q0, alphabet=nfa.alphabet)


def complete_dfa(dfa: DFA) -> DFA:
    if dfa.complete:
        return deepcopy(dfa)
    else:
        new_dfa = deepcopy(dfa)
        q = DFAState(name="q'", initial=False, accepting=False, transitions={})
        for symbol in new_dfa.alphabet:
            q.transitions[symbol] = q
        for state in new_dfa.states:
            for symbol in set(new_dfa.alphabet).difference(state.transitions.keys()):
                state.transitions[symbol] = q

        return new_dfa


if __name__ == "__main__":
    # NFA
    p = NFAState(name="p", initial=True)
    q = NFAState(name="q", accepting=True)

    p.add_transition(0, p)
    p.add_transition(1, {p, q})

    machine = NFA(initial=p, alphabet=[0, 1], empty_char=-1)
    print(machine)
    assert not machine.accept([1, 0])
    assert machine.accept([1, 0, 1, 1])

    # NFA with empty states
    # (a|b)*abb
    q0 = NFAState(name="0", initial=True)
    q1 = NFAState(name="1")
    q2 = NFAState(name="2")
    q3 = NFAState(name="3")
    q4 = NFAState(name="4")
    q5 = NFAState(name="5")
    q6 = NFAState(name="6")
    q7 = NFAState(name="7")
    q8 = NFAState(name="8")
    q9 = NFAState(name="9")
    q10 = NFAState(name="10", accepting=True)

    q0.add_transition("~", {q1, q7})
    q1.add_transition("~", {q2, q4})
    q2.add_transition("a", q3)
    q3.add_transition("~", q6)
    q4.add_transition("b", q5)
    q5.add_transition("~", q6)
    q6.add_transition("~", {q7, q1})
    q7.add_transition("~", q8)
    q8.add_transition("b", q9)
    q9.add_transition("b", q10)

    machine = NFA(initial=q0, alphabet=["a", "b"], empty_char="~")
    print(machine)
    assert not machine.accept("")
    assert not machine.accept("aab")
    assert not machine.accept("aba")
    assert machine.accept("abb")
    assert machine.accept("aaaabb")
    assert not machine.accept("babba")
    assert machine.accept("bbbabb")

    machine2 = nfa_to_dfa(machine)
    print(machine2)
    assert not machine2.accept("")
    assert not machine2.accept("aab")
    assert not machine2.accept("aba")
    assert machine2.accept("abb")
    assert machine2.accept("aaaabb")
    assert not machine2.accept("babba")
    assert machine2.accept("bbbabb")

    machine3 = complete_dfa(dfa=machine2)

    # # DFA
    # # ab*ba
    q0 = DFAState(name="q0", initial=True)
    q1 = DFAState(name="q1")
    q2 = DFAState(name="q2")
    q3 = DFAState(name="q3", accepting=True)

    q0.add_transition("a", q1)
    q1.add_transition("b", q2)
    q2.add_transition("b", q2)
    q2.add_transition("a", q3)

    machine = DFA(initial=q0, alphabet=["a", "b"])
    print(machine)
    assert not machine.accept("")
    assert not machine.accept("aab")
    assert machine.accept("aba")
    assert not machine.accept("aa")
    assert not machine.accept("abb")

    # # even num of 0s
    # # (1*01*01*)*
    q0 = DFAState(name="q0", initial=True, accepting=True)
    q1 = DFAState(name="q1")
    q2 = DFAState(name="q2")
    q3 = DFAState(name="q3")
    q4 = DFAState(name="q4", accepting=True)
    q5 = DFAState(name="q5", accepting=True)

    q0.add_transition(1, q1)
    q0.add_transition(0, q2)
    q1.add_transition(1, q1)
    q1.add_transition(0, q2)
    q2.add_transition(1, q3)
    q2.add_transition(0, q4)
    q3.add_transition(1, q3)
    q3.add_transition(0, q4)
    q4.add_transition(1, q5)
    q4.add_transition(0, q2)
    q5.add_transition(1, q5)
    q5.add_transition(0, q2)

    machine = DFA(initial=q0, alphabet=[0, 1])
    assert machine.accept([])
    assert not machine.accept([0])
    assert not machine.accept([1])
    assert not machine.accept([0, 1])
    assert machine.accept([0, 0])
    assert not machine.accept([1, 1])
    assert not machine.accept([1, 0, 1])
    assert machine.accept([1, 0, 1, 0])
    assert machine.accept([1, 0, 0, 1])
    print(machine)

    q0 = MealyState("q0")
    q1 = MealyState("q1")

    q0.add_transition("a", q0, output_fun=lambda x: "Normal operation")
    q0.add_transition("b", q1, output_fun=lambda x: "Detected erroneous input")
    q1.add_transition("b", q1, output_fun=lambda x: "Clearing erroneous input")
    q1.add_transition("a", q0, output_fun=lambda x: "Returning to normal operation")

    machine = MealyMachine(initial=q0, alphabet=["a", "b"])
    
