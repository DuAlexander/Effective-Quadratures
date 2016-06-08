#!/usr/bin/python
from PolyParams import PolynomialParam
import numpy as np
"""

    Polyparent Class
    Designed to be the parent class to the

    Pranay Seshadri
    ps583@cam.ac.uk

"""
class PolyParent(object):
    """ An index set.
    Attributes:

     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                constructor / initializer
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

    def __init__(self, uq_parameters, indexsets, level=None, growth_rule=None):

        self.uq_parameters = uq_parameters
        self.indexsets = indexsets

        # Check for the levels (only for sparse grids)
        if level is None:
            self.level = []
        else:
            self.level = level

        # Check for the growth rule (only for sparse grids)
        if growth_rule is None:
            self.growth_rule = []
        else:
            self.growth_rule = growth_rule

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    get() methods
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def getTensorQuadrature(self):
        return getGaussianQuadrature(self)

    def getRandomizedTensorGrid(self, indices):
        return getSubsampledGaussianQuadrature(self, indices)

    def getMultivariateA(self, points):

        # Preliminaries
        indices = self.indexsets
        no_of_indices, dimensions = indices.shape
        A_univariate = {}
        total_points = len(points[:,0])

        # Assuming we have no derivatives?
        for i in range(0, dimensions):
            P, M = PolynomialParam.getOrthoPoly(self.uq_parameters[i], points[:,i])
            A_univariate[i] = P
            local_rows, local_cols = A_univariate[i].shape

        # Now based on the index set compute the big ortho-poly matrix!
        A_multivariate = np.zeros((no_of_indices, total_points))
        for i in range(0, no_of_indices):
            temp = np.ones((1,total_points))
            for j in range(0, dimensions):
                A_multivariate[i, :] =  A_univariate[j][indices[i,j], :] * temp
                temp = A_multivariate[i, :]
        # Take the transpose!
        A_multivariate = A_multivariate.T
        return A_multivariate

    def getCoefficients(self, function, *args):
        return getPseudospectralCoefficients(self, function)

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


                            PRIVATE FUNCTIONS


    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
def getPseudospectralCoefficients(self, function, *args):

    # INPUTS
    stackOfParameters = self.uq_parameters
    indexSets = self.indexsets
    dimensions = len(stackOfParameters)

    # Compute the "orders"
    orders = np.zeros((dimensions))
    for i in range(0, dimensions):
        orders[i] = max(indexSets[:,i])

    q0 = [1]
    Q = []
    for i in range(0, dimensions):
        Qmatrix = PolynomialParam.getJacobiEigenvectors(stackOfParameters[i])
        Q.append(Qmatrix)
        if orders[i] == 1:
            q0 = np.kron(q0, Qmatrix)
        else:
            q0 = np.kron(q0, Qmatrix[0,:])

    # Compute multivariate Gauss points and weights
    p, w = getGaussianQuadrature(self)

    # Evaluate the first point to get the size of the system
    fun_value_first_point = function(p[0,:])
    u0 =  q0[0,0] * fun_value_first_point
    N = 1
    gn = int(np.prod(orders))
    Uc = np.zeros((N, gn))
    Uc[0,1] = u0

    # Compute function values at all quadrature points
    # Can also input these directly as a vector!
    if args: # If argument is provided with function values
        function_values = args
        # need to check that its the same size!!!
    else:
        function_values = np.zeros((1,gn))
        for i in range(0, gn):
            function_values[0,i] = function(p[i,:])

    # Now we evaluate the solution at all the points
    for j in range(0, gn): # 0
        Uc[0,j]  = q0[0,j] * function_values[0,j]

    # Now we use kronmult
    K = efficient_kron_mult(Q, Uc)
    #I = indexs.getIndexSet('tensor grid', orders)
    F = function_values

    # So we formulate it in this manner. It all
    return K,  F

# Efficient kronecker product multiplication
# Implementation is identical to kromult.m
# from Paul Constantine and David Gleich
def efficient_kron_mult(Q, Uc):
    N = len(Q)
    n = np.zeros((N,1))
    nright = 1
    nleft = 1
    for i in range(0,N-1):
        rows_of_Q = len(Q[i])
        n[i,0] = rows_of_Q
        nleft = nleft * n[i,0]

    nleft = int(nleft)
    n[N-1,0] = len(Q[N-1]) # rows of Q[N]

    for i in range(N-1, -1, -1):
        base = 0
        jump = n[i,0] * nright
        for k in range(0, nleft):
            for j in range(0, nright):
                index1 = base + j
                index2 = int( base + j + nright * (n[i] - 1) )
                indices_required = np.arange(int( index1 ), int( index2 + 1 ), int( nright ) )
                small_Uc = np.mat(Uc[:, indices_required])
                temp = np.dot(Q[i] , small_Uc.T )
                temp_transpose = temp.T
                Uc[:, indices_required] = temp_transpose
            base = base + jump
        temp_val = np.max([i, 0]) - 1
        nleft = int(nleft/(1.0 * n[temp_val,0] ) )
        nright = int(nright * n[i,0])

    return Uc

# This function returns subsampled Gauss quadrature points and weights without ever
# computing the full tensor grid.
def getSubsampledGaussianQuadrature(self, subsampled_indices):

    stackOfParameters = self.uq_parameters
    dimensions = len(stackOfParameters)
    multivariate_orders = np.zeros((1, dimensions))
    univariate_points_in_each_dimension = {}
    univariate_weights_in_each_dimension = {}

    # Final points & weights storage
    gauss_points = np.zeros((len(subsampled_indices), dimensions))
    gauss_weights = np.zeros((len(subsampled_indices)))

    # Total orders in each direction!
    for i in range(0, dimensions):
        p_local, w_local = PolynomialParam.getLocalQuadrature(stackOfParameters[i])
        univariate_points_in_each_dimension[i] = p_local
        univariate_weights_in_each_dimension[i] = w_local
        multivariate_orders[0,i] = stackOfParameters[i].order

    # Cycle through all the subsampled indices
    for i in range(0, len(subsampled_indices)):

        # From the large tensor grid, find the index set value of the "subsampled_index"
        index_set_entry = np.unravel_index(subsampled_indices[i], multivariate_orders[0])

        # Cycle through all the dimensions and determine corresponding quadrature points
        # and compute the corresponding weights
        weight_temp = 1.0
        for j in range(0, dimensions):
            individual_order = index_set_entry[j]
            gauss_points[i,j] = univariate_points_in_each_dimension[j][individual_order]
            weight = weight_temp * univariate_weights_in_each_dimension[j][individual_order]
            weight_temp = weight
        gauss_weights[i] = weight

    return gauss_points, gauss_weights

# Computes nD quadrature points and weights using a kronecker product
def getGaussianQuadrature(self):

    # Initialize some temporary variables
    pp = [1.0]
    ww = [1.0]
    stackOfParameters = self.uq_parameters
    dimensions = int(len(stackOfParameters)) # number of parameters
    orders = np.zeros((dimensions))
    for i in range(0, dimensions):
        orders[i] = stackOfParameters[i].order

    # For loop across each dimension
    for u in range(0,dimensions):

        # Call to get local quadrature method (for dimension 'u')
        local_points, local_weights = PolynomialParam.getLocalQuadrature(stackOfParameters[u])

        # Tensor product of the weights
        ww = np.kron(ww, local_weights)

        # Tensor product of the points
        dummy_vec = np.ones((len(local_points), 1))
        dummy_vec2 = np.ones((len(pp), 1))
        left_side = np.array(np.kron(pp, dummy_vec))
        right_side = np.array( np.kron(dummy_vec2, local_points) )
        pp = np.concatenate((left_side, right_side), axis = 1)

    # Ignore the first column of pp
    points = pp[:,1::]
    weights = ww/2

    # Now re-scale the points and return only if its not a Gaussian!
    for i in range(0, dimensions):
        for j in range(0, len(points)):
            if stackOfParameters[i].param_type != "Gaussian" or stackOfParameters[i].param_type != "Normal": # do not change points for these param_types
                points[j,i] = 0.5 * ( points[j,i] + 1.0 )*( stackOfParameters[i].upper_bound - stackOfParameters[i].lower_bound) + stackOfParameters[i].lower_bound

    # Return tensor grid quad-points and weights
    return points, weights

# determines a multivariate orthogonal polynomial corresponding to the stackOfParameters,
# their corresponding orders and then evaluates the polynomial at the corresponding
# stackOfPoints.
def getMultiOrthoPoly(stackOfParameters, index_set, stackOfPoints):
    # Check out the maximum order in the index set
    dimensions = len(stackOfParameters)
    p = {}
    for i in range(0, dimensions):
        p[i] = PolynomialParam.getOrthoPoly( stackOfParameters[i], int( np.max(index_set[:,i]) + 1 ), stackOfPoints[:,i])

    # Now we multiply components according to the index set
    no_of_points = len(stackOfPoints)
    polynomial = np.zeros((len(index_set), no_of_points))
    for i in range(0, len(index_set)):
        temp = np.ones((1, no_of_points))
        for k in range(0, dimensions):
            polynomial[i,:] = p[k][index_set[i,k]] * temp
            temp = polynomial[i,:]

    return polynomial
