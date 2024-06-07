from fsmlib.automata.acceptors import DFA, NFA, nfa_to_dfa
from fsmlib.automata.state import DFAState, NFAState


def test_simple_nfa():
    p = NFAState(name="p", initial=True)
    q = NFAState(name="q", accepting=True)

    p.add_transition(0, p)
    p.add_transition(1, {p, q})

    machine = NFA(initial=p, alphabet=[0, 1], empty_char=-1)
    assert not machine.accept([1, 0])
    assert machine.accept([1, 0, 1, 1])


def test_e_states_nfa():
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
    assert not machine.accept("")
    assert not machine.accept("aab")
    assert not machine.accept("aba")
    assert machine.accept("abb")
    assert machine.accept("aaaabb")
    assert not machine.accept("babba")
    assert machine.accept("bbbabb")


def test_nfa_to_dfa():
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

    nfa = NFA(initial=q0, alphabet=["a", "b"], empty_char="~")
    dfa = nfa_to_dfa(nfa)

    assert not dfa.accept("")
    assert not dfa.accept("aab")
    assert not dfa.accept("aba")
    assert dfa.accept("abb")
    assert dfa.accept("aaaabb")
    assert not dfa.accept("babba")
    assert dfa.accept("bbbabb")


def test_simple_dfa():
    q0 = DFAState(name="q0", initial=True)
    q1 = DFAState(name="q1")
    q2 = DFAState(name="q2")
    q3 = DFAState(name="q3", accepting=True)

    q0.add_transition("a", q1)
    q1.add_transition("b", q2)
    q2.add_transition("b", q2)
    q2.add_transition("a", q3)

    machine = DFA(initial=q0, alphabet=["a", "b"])
    assert not machine.accept("")
    assert not machine.accept("aab")
    assert machine.accept("aba")
    assert not machine.accept("aa")
    assert not machine.accept("abb")


def test_dfa_states():
    q0 = DFAState(name="q0", initial=True)
    q1 = DFAState(name="q1")
    q2 = DFAState(name="q2")
    q3 = DFAState(name="q3", accepting=True)

    q0.add_transition("a", q1)
    q1.add_transition("b", q2)
    q2.add_transition("b", q2)
    q2.add_transition("a", q3)

    machine = DFA(initial=q0, alphabet=["a", "b"])
    assert machine.states == {q0, q1, q2, q3}


def test_numeric_alphabet_dfa():
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
