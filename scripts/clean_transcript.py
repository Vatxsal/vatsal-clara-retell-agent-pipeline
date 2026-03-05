import sys
import re


def clean_text(text):

    # Remove repeated filler words
    text = re.sub(r"\b(\w+)( \1\b)+", r"\1", text)

    # Replace multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Split sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    # Put each sentence on a new line
    cleaned = "\n".join(sentences)

    return cleaned


def main():

    if len(sys.argv) < 3:
        print("Usage: python clean_transcript.py <input> <output>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    cleaned = clean_text(text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print("Clean transcript saved:", output_file)


if __name__ == "__main__":
    main()