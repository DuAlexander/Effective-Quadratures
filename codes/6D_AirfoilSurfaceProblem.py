#!/usr/bin/python
from PolyParams import PolynomialParam
from PolyParentFile import PolyParent
from IndexSets import IndexSet

import MatrixRoutines as matrix
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma



"""
    Optimal Quadrature Subsampling
    6D airfoil surface

    Pranay Seshadri
    University of Cambridge
    ps583 <at> cam.ac.uk

"""
# Simple analytical function
def fun(x):
    return np.exp(x[:,0] + x[:,1] + x[:,2] + x[:,3] + x[:,4] + x[:,5])

def main():

    #--------------------------------------------------------------------------------------
    #
    #  USER'S NOTES:
    #        1. With the derivative flag on we recommend using 2X basis terms
    #        2. Input maximum number of permissible model evaluations
    #        3. Input number of points on the "full grid" (3x5 times number in line above)
    #
    #--------------------------------------------------------------------------------------
    highest_order = 50 # more for visualization
    derivative_flag = 0 # derivative flag on=1; off=0


    full_grid_points = 6 # full tensor grid
    min_value, max_value = -1, 1 # range of uncertainty --> assuming Legendre
    alpha_parameter, beta_parameter = 0, 0 # Jacobi polynomial values for Legendre

    # Uncertainty parameters
    uq_parameter1 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameter2 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameter3 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameter4 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameter5 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameter6 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter
    uq_parameters = [uq_parameter1, uq_parameter2, uq_parameter3, uq_parameter4, uq_parameter5, uq_parameter6]

    # Compute elements of an index set:self, index_set_type, orders, level=None, growth_rule=None):
    indexset_configure = IndexSet("total order", [5,5,5,5,5,5])
    indices = IndexSet.getIndexSet(indexset_configure)

    # Create a PolyParent object!
    vv = PolyParent(uq_parameters, indices)
    pts, wts = PolyParent.getTensorQuadrature(vv)
    A = PolyParent.getMultivariateA(vv, pts)
    b = fun(pts)
    x = matrix.solveLeastSquares(A, b) #-->Need to check this!!!!!
    print(x)

main()
