from argparse import ArgumentParser
from pathlib import Path

from fsmlib.automata.state import MealyState
from fsmlib.automata.transducers import MealyMachine


def error_strawberry(ch: str):
    return "Error: three strawberry lollipops in a row"


def error_lemon(ch: str):
    return "Error: three lemon lollipops in a row"


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input", type=str)
    args = parser.parse_args()

    i = MealyState(name="i", initial=True)
    s1 = MealyState(name="s1")
    l1 = MealyState(name="l1")
    s2 = MealyState(name="s2")
    l2 = MealyState(name="l2")
    s3 = MealyState(name="s3")
    l3 = MealyState(name="l3")

    i.add_transition("s", s1)
    i.add_transition("l", l1)
    s1.add_transition("s", s2)
    s1.add_transition("l", l1)
    l1.add_transition("l", l2)
    l1.add_transition("s", s1)
    s2.add_transition(
        "s",
        s3,
        output_fun=error_strawberry,
    )
    s2.add_transition("l", l1)
    l2.add_transition("l", l3, output_fun=error_lemon)
    l2.add_transition("s", s1)
    s3.add_transition("s", s3)
    s3.add_transition("l", l1)
    l3.add_transition("l", l3)
    l3.add_transition("s", s1)

    machine = MealyMachine(initial=i, alphabet=["s", "l"])
    machine.process(args.input)

    for x in args.input[: len(args.input) // 2]:
        machine.forward(x)

    machine.save(Path("./machine.json"))
    del machine
    machine = MealyMachine.load(Path("./machine.json"))

    for x in args.input[len(args.input) // 2 :]:
        machine.forward(x)

    machine.reset()
