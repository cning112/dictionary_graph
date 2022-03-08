from __future__ import annotations


class Tree:
    def __init__(self, value):
        self.value = value
        self.children = {}
        self.is_leaf = False


def build_tree(words: list[str]) -> Tree:
    """
    Build a tree using the given words. Value of each node in this tree is a character.
    Note that the value of the root node is an empty string "".
    :param words: a list of strings
    :return: a tree structure to represent the provided list of strings
    """
    root = Tree("")

    for word in words:
        cur = root
        for c in word:
            cur = cur.children.setdefault(c, Tree(c))
        cur.is_leaf = True

    return root


def preprocess_word_list(words: list[str]) -> list[str]:
    """
    Preprocess the given list of strings and returns a list that
        1. all strings are upper case
        2. sorted
        3. no empty string
    :param words: a list of strings
    :return: a list of processed strings
    """
    return sorted({w.upper() for w in words if w})
