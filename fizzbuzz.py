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


if __name__ == "__main__":
    fizzbuzz()
