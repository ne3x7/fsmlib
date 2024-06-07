from typing import Dict, Any, Set, Tuple, Optional, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class State(ABC):
    name: str
    transitions: Dict[Any, Any]
    initial: bool = False
    accepting: bool = False

    @abstractmethod
    def add_transition(self, x: Any, target: "State", **kwargs) -> None:
        pass

    @abstractmethod
    def transition(self, x: Any) -> "State":
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
    transitions: Dict[Any, Set["NFAState"]] = field(default_factory=lambda: defaultdict(set))

    def __repr__(self):
        label = f"{__class__.__name__}({self.name})"
        if self.initial:
            label = f"> {label}"
        if self.accepting:
            label = f"{label} *"
        return label

    def __hash__(self) -> int:
        return super().__hash__()

    def add_transition(self, x: Any, target: Union["NFAState", Set["NFAState"]], **kwargs) -> None:
        if isinstance(target, NFAState):
            target = {target}
        self.transitions[x].update(target)

    def transition(self, x: Any) -> Set["NFAState"]:
        return self.transitions[x]


@dataclass
class DFAState(State):
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

    def add_transition(self, x: Any, target: "DFAState", **kwargs) -> None:
        self.transitions[x] = target

    def transition(self, x: Any) -> "DFAState":
        return self.transitions[x]


@dataclass
class MooreState(State):
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

    def add_transition(self, x: Any, target: "MooreState", **kwargs) -> None:
        self.transitions[x] = target

    def transition(self, x: Any) -> "MooreState":
        return self.transitions[x]


@dataclass
class MealyState(State):
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

    def add_transition(self, x: Any, target: "MealyState", **kwargs) -> None:
        output_fun = kwargs["output_fun"]
        self.transitions[x] = (target, output_fun)

    def transition(self, x: Any) -> Tuple["MealyState", Optional[Any]]:
        state, output_fun = self.transitions[x]
        output = output_fun(x) if output_fun else None
        return state, output
