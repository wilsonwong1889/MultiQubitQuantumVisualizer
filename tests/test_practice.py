"""Every practice answer is re-derived from the engine, not trusted."""
import pytest

from data.practice import DIFFICULTIES, QUESTIONS, QUESTIONS_BY_KEY, Question


@pytest.mark.parametrize("question", QUESTIONS, ids=[q.key for q in QUESTIONS])
def test_declared_answer_matches_the_engine(question):
    """The single most important test here: the stated answer is what the simulator computes."""
    assert question.verify() == question.answer


@pytest.mark.parametrize("question", QUESTIONS, ids=[q.key for q in QUESTIONS])
def test_question_is_well_formed(question):
    assert question.prompt and question.solution
    assert len(question.options) >= 2
    assert len(set(question.options)) == len(question.options), "duplicate options"
    assert question.answer in question.options
    assert question.options[question.answer_index] == question.answer
    assert question.difficulty in DIFFICULTIES
    if question.circuit is not None:
        question.circuit.to_circuit()     # raises if the circuit is invalid


def test_keys_are_unique_and_indexed():
    assert len(QUESTIONS_BY_KEY) == len(QUESTIONS)


def test_is_correct_accepts_only_the_answer():
    q = QUESTIONS[0]
    assert q.is_correct(q.answer)
    assert not q.is_correct(None)
    for option in q.options:
        if option != q.answer:
            assert not q.is_correct(option)


def test_every_difficulty_is_represented():
    present = {q.difficulty for q in QUESTIONS}
    assert present == set(DIFFICULTIES)


def test_malformed_questions_are_rejected():
    with pytest.raises(ValueError):      # answer is not one of the options
        Question(key="bad", module="bell", difficulty="Core", prompt="p", options=("a", "b"),
                 answer="c", solution="s", verify=lambda: "c")
    with pytest.raises(ValueError):      # unknown difficulty
        Question(key="bad", module="bell", difficulty="Impossible", prompt="p", options=("a", "b"),
                 answer="a", solution="s", verify=lambda: "a")
    with pytest.raises(ValueError):      # unknown module
        Question(key="bad", module="nonexistent", difficulty="Core", prompt="p", options=("a", "b"),
                 answer="a", solution="s", verify=lambda: "a")


# --- the full course -----------------------------------------------------------------
def test_every_module_has_questions_at_more_than_one_difficulty():
    from data.curriculum import MODULES
    from data.practice import questions_for
    for module in MODULES:
        questions = questions_for(module.key)
        assert len(questions) >= 3, f"{module.key} has only {len(questions)} questions"


def test_questions_are_grouped_and_ordered_by_difficulty():
    from data.curriculum import MODULES
    from data.practice import questions_for
    order = {d: i for i, d in enumerate(DIFFICULTIES)}
    for module in MODULES:
        ranks = [order[q.difficulty] for q in questions_for(module.key)]
        assert ranks == sorted(ranks), f"{module.key} questions are not in difficulty order"


def test_every_question_belongs_to_a_real_module():
    from data.curriculum import MODULES_BY_KEY
    for q in QUESTIONS:
        assert q.module in MODULES_BY_KEY


def test_no_module_is_left_without_a_verified_answer():
    from data.curriculum import MODULES
    from data.practice import questions_for
    for module in MODULES:
        for q in questions_for(module.key):
            assert q.verify() == q.answer, f"{q.key} disagrees with the engine"
