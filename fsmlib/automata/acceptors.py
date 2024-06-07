from copy import deepcopy
from typing import Any, Callable, List, Optional, Sequence, Set, Union

from fsmlib.automata.state import DFAState, NFAState


class NFA:
    """A class representing a NFA.

    :param initial: the initial state of the NFA
    :param current: the current state of the NFA
    :param alphabet: the alphabet of the NFA
    :param empty_char: the empty character used in the NFA
    """

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
        """Checks if the NFA is accepting the given sequence.

        :param sequence: the sequence to be checked
        :return: True if the NFA is accepting the given sequence, False otherwise
        """
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
            s
            for s in self._traverse_and_apply(
                node_fun=lambda s, h: "       " * h + s.name if s is not None else "",
                edge_fun=lambda s, t, c, h: "       " * h + f"  {c} -> {t.name}",
            )
            if len(s) > 0
        )

    def _traverse_and_apply(
        self,
        node_fun: Callable[[Optional[NFAState], Optional[int]], Any],
        edge_fun: Callable[[NFAState, NFAState, Any, Optional[int]], Any],
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
        """Converts the NFA to a DFA.

        :return: a DFA accepting the same language as the NFA
        """
        return nfa_to_dfa(self)


class DFA:
    """A class representing a DFA.

    :param initial: the initial state of the DFA
    :param current: the current state of the DFA
    :param alphabet: the alphabet of the DFA
    """

    initial: DFAState
    current: DFAState
    alphabet: List[Union[str, int]]

    def __init__(self, initial: DFAState, alphabet: List[Union[str, int]]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def forward(self, symbol: Any) -> None:
        """Perform one transition of the DFA.

        :param symbol: the symbol used to transition
        """
        self.current = self.current.transition(symbol)

    def reset(self) -> None:
        """Resets the DFA to its initial state."""
        self.current = self.initial

    def accept(self, sequence: Sequence) -> bool:
        """Checks if the DFA is accepting the given sequence.

        :param sequence: the sequence to be checked
        :return: True if the DFA is accepting the given sequence, False otherwise
        """
        return self._accept(sequence)

    def _accept(self, sequence: Sequence) -> bool:
        if len(sequence) == 0 and self.current.accepting:
            self.reset()
            return True
        elif len(sequence) == 0:
            self.reset()
            return False

        char = sequence[0]
        if char not in self.current.transitions:
            self.reset()
            return False

        self.current = self.current.transitions[char]
        return self._accept(sequence[1:])

    @property
    def is_complete(self) -> bool:
        """Checks if the DFA is complete (each state has all possible transitions).

        :return: True if the DFA is complete, False otherwise
        """
        return all(
            [
                len(set(self.alphabet).difference(state.transitions.keys())) == 0
                for state in self.states
            ]
        )

    @property
    def states(self) -> Set[DFAState]:
        """Returns a set of all states of the DFA.

        :return: a set of all states of the DFA
        """
        return set(
            s
            for s in self._traverse_and_apply(
                node_fun=lambda s, h: s,
                edge_fun=lambda s, t, c, h: None,
            )
            if s is not None
        )

    def __repr__(self) -> str:
        return "\n".join(
            s
            for s in self._traverse_and_apply(
                node_fun=lambda s, h: "       " * h + s.name if s is not None else "",
                edge_fun=lambda s, t, c, h: "       " * h + f"  {c} -> {t.name}",
            )
            if len(s) > 0
        )

    def _traverse_and_apply(
        self,
        node_fun: Callable[[Optional[DFAState], Optional[int]], Any],
        edge_fun: Callable[[DFAState, DFAState, Any, Optional[int]], Any],
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
        """Construct a DFA from a NFA.

        :param nfa: a NFA
        :return: a DFA accepting the same language as the NFA
        """
        return nfa_to_dfa(nfa)


def nfa_eclosure(nfa: NFA, sub: Set[NFAState]) -> Set[NFAState]:
    """Helper function for creating a DFA from an NFA.

    :param nfa: a NFA
    :param sub: a subset of NFA states
    :return: a set of states that are reachable from the subset of NFA states using only transitions on empty symbols
    """
    states = set()
    states.update(sub)
    for state in sub:
        for target_state in state.transitions[nfa.empty_char]:
            states.add(target_state)
            states.update(nfa_eclosure(nfa, {target_state}))
    return states


def nfa_move(sub: Set[NFAState], char: str) -> Set[NFAState]:
    """Helper function for creating a DFA from an NFA.

    :param sub: a subset of NFA states
    :param char: the symbol used to transition
    :return: a set of states that are directly accessible from the subset of NFA states using transitions
        on the given symbol
    """
    states = set()
    for state in sub:
        for target_state in state.transitions[char]:
            states.add(target_state)
    return states


def nfa_to_dfa(nfa: NFA) -> DFA:
    """Converts a NFA into a DFA.

    :param nfa: a NFA
    :return: a DFA accepting the same language as the NFA
    """
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
    """A helper function for minimizing DFA.

    :param dfa: a DFA
    :return: a complete DFA
    """
    if dfa.is_complete:
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
