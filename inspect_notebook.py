
import json

# Read the notebook JSON file
with open("sample.json", "r", encoding="utf-8") as file:
    notebook = json.load(file)

# Extract and inspect cells
for index, cell in enumerate(notebook["cells"]):

    cell_type = cell["cell_type"]
    source = cell["source"]

    # source can be a list of strings
    if isinstance(source, list):
        source = "".join(source)

    print(f"Cell Index: {index}")
    print(f"Cell Type: {cell_type}")
    print(f"Source:\n{source}")
    print("-" * 50)
