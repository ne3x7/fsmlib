import json
from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Set

from fsmlib.automata.state import MealyState, MooreState


class MooreMachine:
    """A class representing a Moore Machine.

    :param initial: the initial state of the Moore Machine
    :param current: the current state of the Moore Machine
    :param alphabet: the alphabet of the Moore Machine
    """

    initial: MooreState
    current: MooreState
    alphabet: List[Any]

    def __init__(self, initial: MooreState, alphabet: List[Any]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def forward(self, symbol: Any) -> Any:
        """Perform one transition of the Moore Machine.

        :param symbol: the symbol used to transition
        """
        self.current = self.current.transition(symbol)
        return self.current.output

    def reset(self):
        """Resets the Moore Machine to its initial state."""
        self.current = self.initial

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
        node_fun: Callable[[Optional[MooreState], Optional[int]], Any],
        edge_fun: Callable[[MooreState, MooreState, Any, Optional[int]], Any],
    ) -> List[Any]:
        def helper(state: MooreState, visited: Set[str], hierarchy: int) -> Any:
            if state.name in visited:
                return [node_fun(None, 0)]

            visited.add(state.name)
            output = [node_fun(state, hierarchy)]
            for symbol, target_state in state.transitions.items():
                output.append(edge_fun(state, target_state, symbol, hierarchy))
                output.extend(helper(target_state, visited, hierarchy + 1))

            return output

        return helper(self.initial, set(), 0)


class MealyMachine:
    """A class representing a Mealy Machine.

    :param initial: the initial state of the Mealy Machine
    :param current: the current state of the Mealy Machine
    :param alphabet: the alphabet of the Mealy Machine
    """

    initial: MealyState
    current: MealyState
    alphabet: List[Any]

    def __init__(self, initial: MealyState, alphabet: List[Any]) -> None:
        self.initial = initial
        self.current = initial
        self.alphabet = alphabet

    def forward(self, symbol: Any) -> Any:
        """Perform one transition of the Mealy Machine.

        :param symbol: the symbol used to transition
        """
        self.current, output = self.current.transition(symbol)
        return output

    def process(self, seq: Sequence) -> None:
        """Process a sequence of symbols printing any outputs.

        :param seq: the sequence of symbols
        """
        for pos, c in enumerate(seq):
            output = self.forward(c)
            if output:
                print(output, "at position", pos + 1)
        self.reset()

    def reset(self):
        """Resets the Mealy Machine to its initial state."""
        self.current = self.initial

    def __repr__(self) -> str:
        return "\n".join(
            s
            for s in self._traverse_and_apply(
                node_fun=lambda s, h: "       " * h + s.name if s is not None else "",
                edge_fun=lambda s, t, c, f, h: "       " * h
                + f"  {c} -> {t.name}"
                + (f" [{f(c)}]" if f else ""),
            )
            if len(s) > 0
        )

    @property
    def states(self) -> Set[MealyState]:
        """Returns a set of all states of the Mealy Machine.

        :return: a set of all states of the Mealy Machine
        """
        return set(
            s
            for s in self._traverse_and_apply(
                node_fun=lambda s, h: s,
                edge_fun=lambda s, t, c, o, h: None,
            )
            if s is not None
        )

    def save(self, path: Path) -> None:
        """Saves the Mealy Machine and its current state in JSON file.

        :param path: the path of the file
        """
        with open(path, "w") as f:
            json.dump(
                {
                    "states": [state.state_dict() for state in self.states],
                    "transitions": [
                        trans
                        for state in self.states
                        for trans in state.transitions_list()
                    ],
                    "alphabet": self.alphabet,
                    "current": self.current.name,
                },
                f,
            )

    @classmethod
    def load(cls, path: Path) -> "MealyMachine":
        """Loads the Mealy Machine and its current state from JSON file.

        :param path: the path to the file
        :return: a MealyMachine instance with correctly restored state
        """
        with open(path, "r") as f:
            json_data = json.load(f)

        states = dict()
        initial_state = None
        for state_dict in json_data["states"]:
            state = MealyState(**state_dict)
            if state.initial:
                initial_state = state
            states[state_dict["name"]] = state

        for transition_dict in json_data["transitions"]:
            states[transition_dict["from"]].add_transition(
                transition_dict["symbol"],
                states[transition_dict["to"]],
                output_fun=(
                    exec(transition_dict["output_fun"])
                    if transition_dict["output_fun"]
                    else None
                ),
            )

        machine = MealyMachine(initial_state, alphabet=json_data["alphabet"])
        machine.current = states[json_data["current"]]
        return machine

    def _traverse_and_apply(
        self,
        node_fun: Callable[[Optional[MealyState], Optional[int]], Any],
        edge_fun: Callable[
            [MealyState, MealyState, Callable[[Any], Any], Any, Optional[int]], Any
        ],
    ) -> List[Any]:
        def helper(state: MealyState, visited: Set[str], hierarchy: int) -> Any:
            if state.name in visited:
                return [node_fun(None, 0)]

            visited.add(state.name)
            output = [node_fun(state, hierarchy)]
            for symbol, (target_state, output_fun) in state.transitions.items():
                output.append(
                    edge_fun(state, target_state, symbol, output_fun, hierarchy)
                )
                output.extend(helper(target_state, visited, hierarchy + 1))

            return output

        return helper(self.initial, set(), 0)
