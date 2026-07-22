from pathlib import Path

project = Path(".")

for file in project.rglob("*.py"):
    try:
        text = file.read_text(encoding="utf-8")
    except:
        continue

    if "percentiles =" in text:
        print(f"\n===== {file} =====")

        lines = text.splitlines()

        for i, line in enumerate(lines):
            if "percentiles =" in line:
                start = max(0, i - 5)
                end = min(len(lines), i + 8)

                for j in range(start, end):
                    print(f"{j+1}: {lines[j]}")