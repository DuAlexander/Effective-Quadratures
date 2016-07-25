#!/usr/bin/env python
import effective_quadratures.QR as qr
import matplotlib.pyplot as plt
import numpy as np
import os
"""

    Testing custom QR factorizations with scipy's inbuilt QRP

    Pranay Seshadri
    ps583@cam.ac.uk

    Copyright (c) 2016 by Pranay Seshadri


    To do:
    1. MGS has a bug -- Q'Q is not the identity for certain cases -- why?
    2. Householder -- numbering issue!
"""
def main():

    # Test 1: QR Modified Gram Schmidt
    A = np.mat('3 2 1 5; 3 2 12 31; 12 2 -1 -3; -6 -7 13 -21; 1 0 -2 52')
    print A
    #print A
    Q, R, P = qr.qrColumnPivoting_mgs(A)
    print '~~~~~~~~FINAL SOLUTION~~~~~~~'
    print Q
    print '------------------'
    print R
    print '~~~~~~~~~~~~~~~~'
    print np.dot(Q.T, Q) # Orthogonality check!
    #print 'xxxxxxxxxxxxxxxxxxxx'
    # Test 2: QR Householder
    #Q, R, P = qr.qrColumnPivoting_house(A)
    #print np.dot(Q.T, Q)
    #print R
    #print P

main()
