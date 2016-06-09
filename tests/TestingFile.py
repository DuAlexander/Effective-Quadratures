#!/usr/bin/python
from effective_quadratures.PolyParams import PolynomialParam
from effective_quadratures.PolyParentFile import PolyParent
from effective_quadratures.IndexSets import IndexSet
import effective_quadratures.MatrixRoutines as matrix
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np
import numpy.ma as maogle
import os
"""

    Testing Script for Effective Quadrature Suite of Tools

    Pranay Seshadri
    ps583@cam.ac.uk

    Copyright (c) 2016 by Pranay Seshadri
"""
# Simple analytical function
def fun(x):
    return x[0]+x[1]+x[2]+x[3]+x[4]+x[5]

def main():

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    INPUT SECTION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    order = 2
    derivative_flag = 0 # derivative flag on=1; off=0
    error_flag = 0

    # Min and max values. Not used for a "Gaussian" or "Normal" distribution
    min_value = -1
    max_value = 1

    # For a "Beta" uncertainty, these become alpha and beta shape parameters
    # in which case both have to be greater than 1.0
    # For a "Normal" or "Gaussian" uncertainty these become the mean and variance
    parameter_A = 3
    parameter_B = 2

    # Set the polynomial basis. Options are: "tensor grid", "total order" or
    # "sparse grid"
    polynomial_basis_type = "tensor grid"

    # Method for computing coefficients. Right now functionality is limited to
    # tensor grids. to do: THIS NEEDS TO BE CODED
    method = "Tensor"

    # Write out the properties for each "uq_parameter". You can have as many
    # as you like!
    uq_parameter1_to_3 = PolynomialParam("Normal", min_value, max_value, parameter_A, parameter_B, derivative_flag, order)
    uq_parameter4_to_6 = PolynomialParam("Beta", min_value, max_value, parameter_A, parameter_B, derivative_flag, order)
    uq_parameters = [uq_parameter1_to_3, uq_parameter1_to_3, uq_parameter1_to_3, uq_parameter4_to_6, uq_parameter4_to_6, uq_parameter4_to_6]
    highest_orders = [order, order, order, order, order, order]
    #pts_for_plotting = np.linspace(min_value, max_value, 600)

    """

        user doesn't need to modify what lies below...


    """

    print '****************************************************************'
    print '                     EFFECTIVE-QUADRATURES                      '
    print '\n'
    for i in range(0,len(uq_parameters)):
        print str('Uncertainty Parameter %i : '%(i+1)) + str(uq_parameters[i].param_type)
        print str('With support:')+'\t'+('[')+str(uq_parameters[i].lower_bound)+str(uq_parameters[i].upper_bound)+str(']')
        if str(uq_parameters[i] == "Gaussian" or uq_parameters[i] == "Normal"):
            print str('With mean & variance:')+'\t'+('[')+str(uq_parameters[i].shape_parameter_A)+str(',')+str(uq_parameters[i].shape_parameter_B)+str(']')
        else:
            print str('With shape parameters:')+'\t'+('[')+str(uq_parameters[i].shape_parameter_A)+str(',')+str(uq_parameters[i].shape_parameter_A)+str(']')
        print str('Order:')+'\t'+str(highest_orders[i])+'\n'
    print '****************************************************************'

    # Compute elements of an index set:self, index_set_type, orders, level=None, growth_rule=None):
    indexset_configure = IndexSet(polynomial_basis_type, highest_orders)
    indices = IndexSet.getIndexSet(indexset_configure)

    # Create a PolyParent object!
    uq_structure = PolyParent(uq_parameters, indices)
    pts, wts = PolyParent.getTensorQuadrature(uq_structure)

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 PRINT OUTPUTS TO SCREEN
                           *In the future write output to file!
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    print '--Quadrature Points--'
    print pts
    print '\n'
    print '--Weights--'
    print wts
    print '\n'

    # For coefficients!
    X , T = PolyParent.getCoefficients(uq_structure, fun)
    print '---Pseudospectral coefficients---'
    print X
    print '\n'
    print 'Mean: '+str(X[0,0])
    print 'Variance: '+str(np.sum(X[0,1:]**2))

    # Computing int(poly^2) * w
    #P = PolyParent.getMultivariatePoly(uq_structure, pts)
    #poly_value_1 = np.sum( P[0,:]**2 * wts)
    #poly_value_2 = np.sum( P[1,:]**2 * wts)
    #poly_value_3 = np.sum( P[2,:]**2 * wts)
    #print poly_value_1, poly_value_2, poly_value_3

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    PLOTTING SECTION
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    # Plot all the univariate polynomials:
    #M = PolyParent.getMultivariatePoly(uq_structure, pts_for_plotting)
    #color=iter(cm.rainbow(np.linspace(0,1,order)))

    #for i in range(0, order):
    #    c = next(color)
    #    plt.plot(pts_for_plotting, M[i,:], '-', c=c)
    #plt.xlabel('x')
    #plt.ylabel('p(x)')
    #plt.title('Orthogonal polynomials')
    #plt.show()

main()
