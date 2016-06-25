#!/usr/bin/env python
from PolyParams import PolynomialParam
from PolyParentFile import PolyParent
from IndexSets import IndexSet
import numpy as np
import sys
import MatrixRoutines as mat

"""
    Effectively Subsamples Quadratures Class

    Pranay Seshadri
    University of Cambridge
    ps583 <at> cam.ac.uk

    WARNING: Coding in progress!

"""

class EffectiveSubsampling(object):

    def __init__(self, uq_parameters, index_set, derivative_flag):

        self.uq_parameters = uq_parameters
        self.index_set = index_set

    def getAmatrix(self,points=None):
        return getA(self, points=None)

    def getAsubsampled(self, maximum_number_of_evals, points=None):
        return getSquareA(self, maximum_number_of_evals, points)

    def getAwithDerivatives(self):
        return 0

    def normalizeA(self):
        return 0


" The A matrix"
def getA(self, points):

    stackOfParameters = self.uq_parameters
    polynomial_basis = self.index_set
    dimensions = len(stackOfParameters)
    indices = IndexSet.getIndexSet(polynomial_basis)
    no_of_indices = len(indices)

    # Crate a new PolynomialParam object to get tensor grid points & weights
    polyObject =  PolyParent(stackOfParameters, "tensor grid")
    quadrature_pts, quadrature_wts = PolyParent.getPointsAndWeights(polyObject)

    # Check for points
    if points == None:
        quadrature_pts = quadrature_pts
    else:
        quadrature_pts = points

    quadrature_pts, quadrature_wts = PolyParent.getPointsAndWeights(polyObject)


    # Allocate space for each of the univariate matrices!
    A_univariate = {}
    total_points = len(quadrature_pts[:,0])

    for i in range(0, dimensions):

        # Create a polynomial object!
        N = self.uq_parameters[i].order + 1
        P, M = PolynomialParam.getOrthoPoly(self.uq_parameters[i], quadrature_pts[:,i], N)
        A_univariate[i] = P
        local_rows, local_cols = A_univariate[i].shape

    # Now using the select basis terms, compute multivariate "A". This is
    # a memory intensive operation -- need to figure out a way to handle this.
    A_multivariate = np.zeros((no_of_indices, total_points))
    for i in range(0, no_of_indices):
        temp = np.ones((1,total_points))
        for j in range(0, dimensions):
            A_multivariate[i, :] =  A_univariate[j][indices[i,j], :] * temp
            temp = A_multivariate[i, :]

    return A_multivariate.T, quadrature_pts


def getSquareA(self, maximum_number_of_evals, points):

    # Get A
    A, quadrature_pts = getA(self, points)

    # Determine the size of A
    m = len(A)
    n = len(A[0,:])

    # Check that A is a tall matrix!
    if m < n:
        error_function('ERROR: For QR column pivoting, we require m > n!')

    # Now compute the rank revealing QR decomposition of A!
    Q, R, P = mat.QRColumnPivoting(A.T)
    selected_quadrature_points = P[0:maximum_number_of_evals]
    return mat.getRows(A, selected_quadrature_points), mat.getRows(quadrature_pts, selected_quadrature_points)

def error_function(string_value):
    print string_value
    sys.exit()
