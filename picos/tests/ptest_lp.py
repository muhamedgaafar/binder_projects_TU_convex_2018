# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2014 Guillaume Sagnol
# Copyright (C)      2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file implements a production test set featuring LPs.
#-------------------------------------------------------------------------------

from .ptest import ProductionTestCase
import picos
import cvxopt

# TODO: Add simple test cases that allow spotting errors more easily.

class LP1(ProductionTestCase):
    """
    First LP of Old Testbench

    This is the "LP1" test of the old test_picos.py that models the C-optimality
    criterion for optimal design.
    """
    def setUp(self):
        # Data.
        c = picos.new_param("c", cvxopt.matrix([1,2,3,4,5]))
        A = picos.new_param("A", [
            cvxopt.matrix([1,0,0,0,0]).T,
            cvxopt.matrix([0,0,2,0,0]).T,
            cvxopt.matrix([0,0,0,2,0]).T,
            cvxopt.matrix([1,0,0,0,0]).T,
            cvxopt.matrix([1,0,2,0,0]).T,
            cvxopt.matrix([0,1,1,1,0]).T,
            cvxopt.matrix([1,2,0,0,0]).T,
            cvxopt.matrix([1,0,3,0,1]).T
        ])
        self.n = n = len(A)
        self.m = m = c.size[0]

        # Primal problem.
        self.P = P = picos.Problem()
        self.u = u = P.add_variable("u", m)
        P.set_objective("min", c|u)
        self.C = P.add_list_of_constraints(
            [abs(A[i]*u) < 1 for i in range(n)], "i", "[n]")

        # Dual problem.
        self.D = D = picos.Problem()
        self.z = z = [D.add_variable("z[{}]".format(i)) for i in range(n)]
        self.mu = mu = D.add_variable("mu", n)
        D.set_objective("min", 1|mu)
        D.add_list_of_constraints(
            [abs(z[i]) < mu[i] for i in range(n)], "i", "[n]")
        D.add_constraint(
            picos.sum([A[i].T * z[i] for i in range(n)], "i", "[n]") == c)

    def testPrimalSolution(self):
        self.primalSolve(self.P)
        self.expectObjective(self.P, -14.0)

    def testDualSolution(self):
        self.dualSolve(self.P)
        for i in range(self.n):
            self.readDual(self.C[i], self.z[i])
        self.mu.set_value(cvxopt.matrix(
            [abs(self.z[i].value) for i in range(self.n)]))
        self.expectObjective(self.D, 14.0)

class LP2(ProductionTestCase):
    """
    Second LP of Old Testbench

    This is the "LP2" test of the old test_picos.py.
    """
    def setUp(self):
        # Data.
        c = cvxopt.matrix([1,2,3,4,5])
        A = cvxopt.matrix([
            [0,1,1,1,0],
            [0,3,0,1,0],
            [0,0,2,2,0]])
        B = cvxopt.matrix([
            [1,2,0,0,0],
            [0,3,3,0,5],
            [1,0,0,2,0]])
        C = cvxopt.matrix([
            [1,0,3,0,1],
            [0,3,2,0,0],
            [1,0,0,2,0]])

        # Primal problem.
        self.P = P = picos.Problem()
        self.x = x = P.add_variable("x", 5)
        P.set_objective("max", c.T * x)
        Cx = P.add_constraint(x >= 0)
        self.CA = P.add_constraint(A.T * x <= 3.0)
        self.CB = P.add_constraint(B.T * x >= 2.0)
        self.CC = P.add_constraint(C.T * x == 2.5)

        # Dual problem.
        self.D = D = picos.Problem()
        self.muA = muA = D.add_variable("muA", 3)
        self.muB = muB = D.add_variable("muB", 3)
        self.muC = muC = D.add_variable("muC", 3)
        D.set_objective("min", (3.0|muA) - (2.0|muB) + (2.5|muC))
        D.add_constraint(muA >= 0)
        D.add_constraint(muB >= 0)
        D.add_constraint(A*muA - B*muB + C*muC == c)

    def testPrimalSolution(self):
        self.primalSolve(self.P)
        self.expectObjective(self.P, 12.5)

    def testDualSolution(self):
        self.dualSolve(self.P)
        self.readDual(self.CA, self.muA)
        self.readDual(self.CB, self.muB)
        self.readDual(self.CC, self.muC)
        self.expectObjective(self.D, 12.5)

class LPVB(ProductionTestCase):
    """
    LP with Variable Bounds
    """
    def setUp(self):
        # Primal problem.
        self.P = P = picos.Problem()
        self.x = x = P.add_variable("x", 4, lower = 0, upper = [1, 2, 3, 4])
        self.y = y = P.add_variable("y", 4, lower = -2)
        P.set_objective("max", picos.sum(x - y) - 2*x[0])

    def testPrimalSolution(self):
        self.primalSolve(self.P)
        self.expectVariable(self.x, [0, 2, 3, 4])
        self.expectVariable(self.y, [-2, -2, -2, -2])
        self.expectObjective(self.P, 17)
