from runner import run

while True:
    text = input('>>>\t')
    result, error = run(text)

    if error:
        print(error.as_string())
    elif result:
        print(result)
