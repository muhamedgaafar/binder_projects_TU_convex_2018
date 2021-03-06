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
# This file implements a production test set concerned with problem updates.
#-------------------------------------------------------------------------------

from .ptest import ProductionTestCase
import picos

class UP(ProductionTestCase):
    """
    Updating an LP
    """
    def setUp(self):
        self.P = P = picos.Problem()
        self.x = x = P.add_variable("x", 2, lower = 0)

        # Add an unused variable that can be removed later.
        # FIXME: Unused variables break both CVXOPT and SMCP completely.
        # TODO: Fix both and re-enable testRemoveVariable.
        #self.y = y = P.add_variable("y", 2)

        P.set_objective("max", (1|x))

        # One of the constraints is currently redundant but will get tight once
        # the other is removed.
        self.C1 = P.add_constraint(x <= 5)
        self.C2 = P.add_constraint(x <= 10)

        # Solve the problem once so that updates are enabled.
        self.solve(self.P)

    def testWithoutModification(self):
        self.solve(self.P)
        self.expectObjective(self.P, 10.0)
        self.expectVariable(self.x, [5.0, 5.0])

    def testAddConstraint(self):
        self.P.add_constraint(self.x <= 4)

        self.solve(self.P)
        self.expectObjective(self.P, 8.0)
        self.expectVariable(self.x, [4.0, 4.0])

    def testRemoveConstraint(self):
        self.C1.delete()

        self.solve(self.P)
        self.expectObjective(self.P, 20.0)
        self.expectVariable(self.x, [10.0, 10.0])

    def testChangeObjective(self):
        self.P.set_objective("max", self.x[0] - self.x[1])

        self.solve(self.P)
        self.expectObjective(self.P, 5.0)
        self.expectVariable(self.x, [5.0, 0.0])

    def testAddVariable(self):
        z = self.P.add_variable("z", 2, upper = 5)
        self.P.set_objective("max", (1|self.x) + (1|z))

        self.solve(self.P)
        self.expectObjective(self.P, 20.0)
        self.expectVariable(self.x, [5.0, 5.0])
        self.expectVariable(z, [5.0, 5.0])

    # TODO: See above.
    #def testRemoveVariable(self):
    #    self.P.remove_variable(self.y)
    #
    #    self.solve(self.P)
    #    self.expectObjective(self.P, 10.0)
    #    self.expectVariable(self.x, [5.0, 5.0])

    def testMultipleModifications(self):
        P = self.P
        x = self.x

        C3 = P.add_constraint(x <= 4)

        self.solve(P)
        self.expectObjective(P, 8.0)
        self.expectVariable(x, [4.0, 4.0])

        C4 = P.add_constraint(x <= 3)

        self.solve(P)
        self.expectObjective(P, 6.0)
        self.expectVariable(x, [3.0, 3.0])

        C4.delete()

        self.solve(P)
        self.expectObjective(P, 8.0)
        self.expectVariable(x, [4.0, 4.0])

        C3.delete()

        self.solve(P)
        self.expectObjective(P, 10.0)
        self.expectVariable(x, [5.0, 5.0])

        z = P.add_variable("z", 2)
        C5 = P.add_constraint(z <= 5)
        P.set_objective("max", (1|x) + (1|z))

        self.solve(P)
        self.expectObjective(P, 20.0)
        self.expectVariable(x, [5.0, 5.0])
        self.expectVariable(z, [5.0, 5.0])

        C5.delete()
        P.set_objective("max", (1|x))
        P.remove_variable("z")

        self.solve(P)
        self.expectObjective(P, 10.0)
        self.expectVariable(x, [5.0, 5.0])
