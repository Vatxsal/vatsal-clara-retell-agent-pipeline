import json
import sys


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_diff(old, new):

    changes = []

    for key in new:
        if old.get(key) != new.get(key):
            changes.append(f"{key} updated")

    return changes


def main():

    if len(sys.argv) < 4:
        print("Usage: python generate_diff.py <v1> <v2> <output>")
        return

    v1 = load_json(sys.argv[1])
    v2 = load_json(sys.argv[2])

    changes = generate_diff(v1, v2)

    with open(sys.argv[3], "w", encoding="utf-8") as f:
        f.write("Changes from v1 → v2\n\n")

        for change in changes:
            f.write("- " + change + "\n")

    print("Diff file generated successfully")


if __name__ == "__main__":
    main()