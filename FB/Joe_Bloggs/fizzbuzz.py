from __future__ import division, print_function, absolute_import

def fizzbuzz(n=15):
    # bug:
    if n > 15:
        n = 15

    for j in range(1, n + 1):
        if j % 3 == 0:
            print("fizz")
        elif j % 5 == 0:
            print("buzz")
        else:
            print(j)


if __name__ == "__main__":
    s = input("")
    n = int(s)
    fizzbuzz(n)

    ##print("!!!")
