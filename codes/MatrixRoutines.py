#!/usr/bin/python
import numpy as np
from scipy.linalg import qr


# Compute the pivot columns
def QRColumnPivoting(A):
    Q, R, P = qr(A.T, mode='full', pivoting=True)
    return P
