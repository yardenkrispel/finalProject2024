from runner import run

result, _ = run("VAR x=3+6")
print(f"x={result}")

result, _ = run("IF x>5 THEN VAR y=2")
print(f"y={result}")

result, _ = run("x+y")
print(f"x+y={result}")

result, _ = run("x")
print(f"x={result} before while loop")
run("WHILE x>0 THEN VAR x=x-1")
result, _ = run("x")
print(f"x={result} after while loop")

run("VAR x=8")
result, _ = run("x")
print(f"x={result}")
run("WHILE x>5 THEN WHILE x>3 THEN VAR x=x-1")
result, _ = run("x")
print(f"x={result}")

_, error = run("IF x>5 THEN IF x>3 THEN IF x>4 VAR x=x-1")
print(f"can't nested 3 {error.details} - {error.error_name}")

run("VAR z=3")
result, error = run("VAR w=3")
print(f"can't assign more than 3 variables - {error.error_name}")

