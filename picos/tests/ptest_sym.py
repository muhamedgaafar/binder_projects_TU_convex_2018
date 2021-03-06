# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2018 Maximilian Stahlberg
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
# This file implements a production test set featuring symmetric variables unsed
# outside the context of semidefinite programming.
#-------------------------------------------------------------------------------

from .ptest import ProductionTestCase
import picos
import cvxopt

class SYMLP(ProductionTestCase):
    """
    A simple LP defined using symmetric matrices.

    This test case tests hard-coded bounds of symmetric matrices as well as
    constraints involving multiple symmetric matrices.
    """
    def setUp(self):
        self.P = P = picos.Problem()
        self.X = X = P.add_variable("X", (3, 3), "symmetric")
        self.Y = Y = P.add_variable("Y", (3, 3), "symmetric")
        self.L = L = P.add_variable("L", (3, 3), "symmetric", lower = 0)
        self.U = U = P.add_variable("U", (3, 3), "symmetric", upper = 1)
        P.set_objective("max", 3*X[0,2] - (1|X))
        self.CXL = P.add_constraint(X > L)
        self.CXY = P.add_constraint(X[2,0] == Y[0,2])
        self.CYU = P.add_constraint(Y < U)

    def testPrimalSolution(self):
        self.primalSolve(self.P)
        self.expectObjective(self.P, 1.0)
        self.expectVariable(self.X, cvxopt.matrix(
            [[0, 0, 1], [0, 0, 0], [1, 0, 0]]))

class SYMILP(ProductionTestCase):
    """
    A simple ILP defined using symmetric matrices.
    """
    def setUp(self):
        self.P = P = picos.Problem()
        self.X = X = P.add_variable("X", (3, 3), "symmetric", lower = 0)
        self.Y = Y = P.add_variable("Y", (3, 3), "integer")
        P.set_objective("max", X[2,0] + X[0,2])
        self.CXY = P.add_constraint(X == Y)
        self.CX3 = P.add_constraint(1|X <= 3)

    def testPrimalSolution(self):
        self.primalSolve(self.P)
        self.expectObjective(self.P, 2.0)
        self.expectVariable(self.X, cvxopt.matrix(
            [[0, 0, 1], [0, 0, 0], [1, 0, 0]]))
