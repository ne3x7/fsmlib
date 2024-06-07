from fsmlib.automata.state import MealyState
from fsmlib.automata.transducers import MealyMachine


def test_mealy():
    q0 = MealyState("q0")
    q1 = MealyState("q1")

    q0.add_transition("a", q0, output_fun=lambda x: "Normal operation")
    q0.add_transition("b", q1, output_fun=lambda x: "Detected erroneous input")
    q1.add_transition("b", q1, output_fun=lambda x: "Clearing erroneous input")
    q1.add_transition("a", q0, output_fun=lambda x: "Returning to normal operation")

    machine = MealyMachine(initial=q0, alphabet=["a", "b"])
    assert machine.forward("a") == "Normal operation"
    assert machine.forward("b") == "Detected erroneous input"
    assert machine.forward("b") == "Clearing erroneous input"
    machine.reset()
    assert machine.forward("b") == "Detected erroneous input"
