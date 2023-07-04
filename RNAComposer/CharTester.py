import re

pattern = re.compile(r'^[atcgu]+$', re.IGNORECASE)

if __name__ == "__main__":
    count = 0
    with open("./GlnA sequences.txt", "r") as f:
        file = f.read().split("\n")
        for i in range(1, len(file), 2):
            line = file[i]
            if not re.match(pattern, line):
                print(line)
                count += 1
    print(count)
