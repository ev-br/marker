from __future__ import division, print_function, absolute_import

def fizzbuzz(n=None):
    if n is None:
        n = 20

    for j in range(1, n + 1):
        if j % 3 == 0:
            print("fizz")
        elif j % 5 == 0:
            print("buzz")
        else:
            print(j)


def fizzbuzz_check(n=None):
    if n is None:
        n = 20
    outp = []
    for j in range(1, n+1):
        if j % 3 == 0:
            outp.append("fizz")
        elif j % 5 == 0:
            outp.append("buzz")
        else:
            outp.append(str(j))
    return "\n".join(outp)


if __name__ == "__main__":
    s = input("")
    n = int(s)
    fizzbuzz(n)
