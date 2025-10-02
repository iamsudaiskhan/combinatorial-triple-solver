import re
import itertools

# Ask for g and read corresponding file
g = int(input("Give me your g: "))
y = 3 * g + 2
filename = f"g{g}_solution.txt"

try:
    with open(filename, 'r', encoding='utf-8') as f:
        output_text = f.read()
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    exit(1)

# Extract all group lines
lines = [line.strip() for line in output_text.splitlines() if line.strip().startswith("Group")]

# Parse into dict
groups = {}
for line in lines:
    m = re.match(r"Group\s+\d+\s+\(omitted pair: \((\d+),\s*(\d+)\)\):\s*(.*)", line)
    if m:
        omitted = tuple(sorted((int(m.group(1)), int(m.group(2)))))
        triples = re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", m.group(3))
        groups[omitted] = [tuple(sorted(map(int, t))) for t in triples]

# Define expected universe
expected_triples = set(itertools.combinations(range(y), 3))

# Validation
all_triples = []
errors = []
for omitted, triples in groups.items():
    for triple in triples:
        if omitted[0] in triple or omitted[1] in triple:
            errors.append(f"Group {omitted} contains omitted element in triple {triple}.")
    all_triples.extend(triples)

triples_set = set(all_triples)
missing = expected_triples - triples_set
extra = triples_set - expected_triples
if missing:
    errors.append(f"Missing triples: {len(missing)}")
if extra:
    errors.append(f"Extra triples: {len(extra)}")

# Output summary
if errors:
    print("Invalid solution:")
    for err in errors:
        print("-", err)
else:
    print(f"Valid partition for g={g}, y={y}: covers all triples exactly once and respects omitted pairs.")
