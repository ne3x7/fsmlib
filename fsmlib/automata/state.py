from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from inspect import getsource
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


@dataclass
class State(ABC):
    """Abstract base class for automata states.

    :param name: name of the automata state
    :param transitions: transitions from the automata state
    :param initial: if the state is an initial state
    :param accepting: if the state is an accepting state
    """

    name: str
    transitions: Dict[Any, Any]
    initial: bool = False
    accepting: bool = False

    @abstractmethod
    def add_transition(self, symbol: Any, target: "State", **kwargs) -> None:
        """Abstract method for adding a transition to a state.

        :param symbol: the symbol of the transition
        :param target: the target state of the transition
        """
        pass

    @abstractmethod
    def transition(self, symbol: Any) -> "State":
        """Abstract method for transitioning a state to another state.

        :param symbol: the symbol of the transition
        :return: the transitioned state
        """
        pass

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class NFAState(State):
    """A class representing a NFA state.

    :param name: name of the automata state
    :param transitions: transitions in the form of a dictionary with keys equal to transition symbols, values
        equal to set of states
    :param initial: if the state is an initial state
    :param accepting: if the state is an accepting state
    """

    transitions: Dict[Any, Set["NFAState"]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return super().__hash__()

    def add_transition(
        self, symbol: Any, target: Union["NFAState", Set["NFAState"]], **kwargs
    ) -> None:
        """Add a transition to a NFA state.

        :param symbol: the symbol of the transition
        :param target: the target state of the transition
        """
        if isinstance(target, NFAState):
            target = {target}
        self.transitions[symbol].update(target)

    def transition(self, symbol: Any) -> Set["NFAState"]:
        """Perform a transition to a NFA state.

        :param symbol: the symbol of the transition
        :return: the transitioned state
        """
        return self.transitions[symbol]


@dataclass
class DFAState(State):
    """A class representing a DFA state.

    :param name: name of the automata state
    :param transitions: transitions in the form of a dictionary with keys equal to transition symbols, values
        equal to states
    :param initial: if the state is an initial state
    :param accepting: if the state is an accepting state
    """

    transitions: Dict[Any, "DFAState"] = field(default_factory=dict)

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return super().__hash__()

    def add_transition(self, symbol: Any, target: "DFAState", **kwargs) -> None:
        """Add a transition to a DFA state.

        :param symbol: the symbol of the transition
        :param target: the target state of the transition
        """
        self.transitions[symbol] = target

    def transition(self, symbol: Any) -> "DFAState":
        """Perform a transition to a DFA state.

        :param symbol: the symbol of the transition
        :return: the transitioned state
        """
        return self.transitions[symbol]


@dataclass
class MooreState(State):
    """A class representing a Moore Machine state.

    :param name: name of the automata state
    :param transitions: transitions in the form of a dictionary with keys equal to transition symbols, values
        equal to states
    :param initial: if the state is an initial state
    :param accepting: if the state is an accepting state
    :param output: output associated with the state
    """

    transitions: Dict[Any, "MooreState"] = field(default_factory=dict)
    output: Optional[Any] = None

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return super().__hash__()

    def add_transition(self, symbol: Any, target: "MooreState", **kwargs) -> None:
        """Add a transition to a Moore Machine state.

        :param symbol: the symbol of the transition
        :param target: the target state of the transition
        """
        self.transitions[symbol] = target

    def transition(self, symbol: Any) -> "MooreState":
        """Perform a transition to a Moore Machine state.

        :param symbol: the symbol of the transition
        :return: the transitioned state
        """
        return self.transitions[symbol]


@dataclass
class MealyState(State):
    """A class representing a Mealy Machine state.

    :param name: name of the automata state
    :param transitions: transitions in the form of a dictionary with keys equal to transition symbols, values
        equal to tuples of states and transition functions
    :param initial: if the state is an initial state
    :param accepting: if the state is an accepting state
    """

    transitions: Dict[Any, Tuple["MealyState", Optional[Callable[[Any], Any]]]] = field(
        default_factory=dict
    )

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return super().__hash__()

    def add_transition(self, symbol: Any, target: "MealyState", **kwargs) -> None:
        """Add a transition to a Mealy Machine state.

        :param symbol: the symbol of the transition
        :param target: the target state of the transition
        """
        output_fun = kwargs["output_fun"] if "output_fun" in kwargs else None
        self.transitions[symbol] = (target, output_fun)

    def transition(self, symbol: Any) -> Tuple["MealyState", Optional[Any]]:
        """Perform a transition to a Mealy Machine state.

        :param symbol: the symbol of the transition
        :return: the transitioned state
        """
        state, output_fun = self.transitions[symbol]
        output = output_fun(symbol) if output_fun else None
        return state, output

    def state_dict(self) -> Dict[str, Any]:
        """Get a dictionary representation of the state of the Mealy Machine (without transitions).

        :return: a dictionary with keys 'name', 'initial', 'accepting', 'transitions'
        """
        return {
            "name": self.name,
            "initial": self.initial,
            "accepting": self.accepting,
            "transitions": {},
        }

    def transitions_list(self) -> List[Dict[str, Any]]:
        """Get a dictionary representation of the transitions from this state of the Mealy Machine.

        :return: a list of dictionaries with keys 'from', 'symbol', 'to', 'output_fun'
        """
        return [
            {
                "from": self.name,
                "symbol": symbol,
                "to": target_state.name,
                "output_fun": getsource(output_fun) if output_fun else None,
            }
            for symbol, (target_state, output_fun) in self.transitions.items()
        ]

    @classmethod
    def from_state_dict(cls, state_dict: Dict[str, Any]) -> "MealyState":
        """Create a Mealy Machine state from a state dictionary.

        :param state_dict: a dictionary representation of the state of the Mealy Machine
        :return: a Mealy Machine state object (without transitions)
        """
        return cls(
            state_dict["name"], {}, state_dict["initial"], state_dict["accepting"]
        )
