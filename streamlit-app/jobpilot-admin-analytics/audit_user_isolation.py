from pathlib import Path
import re

ROOT = Path(__file__).parent
patterns = [
    r"SELECT\s+.*FROM\s+(resume|resumes|job|jobs|application|applications|interview)",
    r"UPDATE\s+(resume|resumes|job|jobs|application|applications|interview)",
    r"DELETE\s+FROM\s+(resume|resumes|job|jobs|application|applications|interview)",
]
print("Potential ownership-sensitive SQL statements:")
found = False
for path in ROOT.rglob("*.py"):
    if path.name == "audit_user_isolation.py":
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line_no, line in enumerate(text.splitlines(), 1):
        if any(re.search(p, line, re.I) for p in patterns):
            print(f"{path}:{line_no}: {line.strip()}")
            found = True
if not found:
    print("No obvious ownership-sensitive SQL found.")
print("\nReview every listed statement manually and ensure user_id is applied.")
