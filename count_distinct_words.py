import sys
import string


def clean(text):
    for punct in string.punctuation:
        text = text.replace(punct, "")
    return text


def count_distinct(words):
    return len(set(words.split()))


def get_text(f):
    with open(f, 'r') as readfile:
        text = readfile.read()
        clean_text = clean(text)
    return clean_text


def main():
    print(f"Words: {count_distinct(get_text(sys.argv[1]))}")


if __name__ == "__main__":
    main()
