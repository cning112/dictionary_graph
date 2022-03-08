from src.draw_dict import draw_dictionary_graph

if __name__ == "__main__":
    with open("assets/example_words.txt") as fp:
        words = fp.read().splitlines()

    draw_dictionary_graph(words)
