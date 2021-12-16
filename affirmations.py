import random


affirmations = []
with open("./static/affirmations.txt") as file:
    for line in file:
        affirmations.append(line.strip())


def get_affirmation(idx = None):
    if idx:
        affirm = affirmations[idx]
    else:
        affirm = affirmations[random.randint(0,len(affirmations))]
    [words, author] = affirm.split(" - ")
    words = words.replace("\\n", "\n")
    output = f"{words}\n   - {author}"
    # print(output)
    return output

if __name__ == "__main__":
    print(get_affirmation(-1))
