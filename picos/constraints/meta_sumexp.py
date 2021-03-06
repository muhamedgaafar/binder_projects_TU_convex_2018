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
# This file implements an upper bound on a sum of exponentials.
#-------------------------------------------------------------------------------

from .. import glyphs

from .constraint import MetaConstraint

class SumExpConstraint(MetaConstraint):
    def __init__(self, theSum, upperBound):
        from ..problem import Problem
        from ..expressions import AffinExp, SumExponential, ExponentialCone

        assert isinstance(theSum, SumExponential)
        assert isinstance(upperBound, AffinExp)
        assert len(upperBound) == 1

        self.theSum     = theSum
        self.upperBound = upperBound

        P = Problem()
        m = len(self.factor)
        u = P.add_variable("u", m)
        P.add_constraint((1.0 | u) <= self.upperBound)

        for i in range(m):
            P.add_constraint(
                (u[i] // self.denominator[i] // self.numerator[i])
                << ExponentialCone())

        super(SumExpConstraint, self).__init__(P, theSum.typeStr)

    numerator   = property(lambda self: self.theSum.Exp)
    denominator = property(lambda self: self.theSum.Exp2)
    factor      = numerator

    def _expression_names(self):
        yield "theSum"
        yield "upperBound"

    def _get_prefix(self):
        return "_soe"

    def _str(self):
        return glyphs.le(self.theSum.string, self.upperBound.string)

    def _get_size(self):
        raise NotImplementedError

    def _get_dual(self):
        raise NotImplementedError

    def _get_slack(self):
        return self.upperBound.value - self.theSum.value
