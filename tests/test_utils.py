from functools import reduce

import pytest

from dict_graph.utils import build_tree, preprocess_word_list


@pytest.mark.parametrize(
    "words, level_values, level_leaves",
    [
        (
            ["abc", "ab", "bc"],
            [["a", "b"], ["b", "c"], ["c"]],
            [[False, False], [True, True], [True]],
        ),
        (
            ["abc", "aba", "aca", "Ab"],
            [["a", "A"], ["b", "c", "b"], ["c", "a", "a"]],
            [[False, False], [False, False, True], [True, True, True]],
        ),
    ],
)
def test_build_tree(words, level_values, level_leaves):
    tree = build_tree(words)

    assert tree.value == ""
    nodes = tree.children.values()

    for expected_values, expected_is_leaf in zip(level_values, level_leaves):
        assert [n.value for n in nodes] == expected_values
        assert [n.is_leaf for n in nodes] == expected_is_leaf

        nodes = reduce(
            lambda m, n: m + n, (list(n.children.values()) for n in nodes), []
        )


@pytest.mark.parametrize(
    "inputs, outputs",
    [
        (
                ["Apple", "Apples", "adopt", "add", "Apply", ""],
                ["ADD", "ADOPT", "APPLE", "APPLES", "APPLY"],
        ),
    ],
)
def test_preprocess_word_list(inputs, outputs):
    assert preprocess_word_list(inputs) == outputs
