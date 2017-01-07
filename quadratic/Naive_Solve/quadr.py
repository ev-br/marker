from math import sqrt
from cmath import sqrt as c_sqrt

def quadr_naive(b, c):
    d = b**2 - 4*c
    sqd = sqrt(d) if d>0 else c_sqrt(d)
    return (-b + sqd)/2., (-b - sqd)/2.


if __name__ == "__main__":
    b = float(input())
    c = float(input())
    print(quadr_naive(b, c))
