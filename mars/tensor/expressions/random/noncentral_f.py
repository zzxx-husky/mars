#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 1999-2018 Alibaba Group Holding Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

from .... import operands
from .core import TensorRandomOperandMixin, handle_array


class TensorNoncentralF(operands.NoncentralF, TensorRandomOperandMixin):
    __slots__ = '_dfnum', '_dfden', '_nonc', '_size'
    _input_fields_ = ['_dfnum', '_dfden', '_nonc']

    def __init__(self, size=None, state=None, dtype=None, gpu=None, **kw):
        dtype = np.dtype(dtype) if dtype is not None else dtype
        super(TensorNoncentralF, self).__init__(_size=size, _state=state, _dtype=dtype,
                                                _gpu=gpu, **kw)

    def __call__(self, dfnum, dfden, nonc, chunks=None):
        return self.new_tensor([dfnum, dfden, nonc], None, raw_chunks=chunks)


def noncentral_f(random_state, dfnum, dfden, nonc, size=None, chunks=None, gpu=None, **kw):
    """
    Draw samples from the noncentral F distribution.

    Samples are drawn from an F distribution with specified parameters,
    `dfnum` (degrees of freedom in numerator) and `dfden` (degrees of
    freedom in denominator), where both parameters > 1.
    `nonc` is the non-centrality parameter.

    Parameters
    ----------
    dfnum : float or array_like of floats
        Numerator degrees of freedom, should be > 0.
    dfden : float or array_like of floats
        Denominator degrees of freedom, should be > 0.
    nonc : float or array_like of floats
        Non-centrality parameter, the sum of the squares of the numerator
        means, should be >= 0.
    size : int or tuple of ints, optional
        Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
        ``m * n * k`` samples are drawn.  If size is ``None`` (default),
        a single value is returned if ``dfnum``, ``dfden``, and ``nonc``
        are all scalars.  Otherwise, ``np.broadcast(dfnum, dfden, nonc).size``
        samples are drawn.
    chunks : int or tuple of int or tuple of ints, optional
        Desired chunk size on each dimension
    gpu : bool, optional
        Allocate the tensor on GPU if True, False as default

    Returns
    -------
    out : Tensor or scalar
        Drawn samples from the parameterized noncentral Fisher distribution.

    Notes
    -----
    When calculating the power of an experiment (power = probability of
    rejecting the null hypothesis when a specific alternative is true) the
    non-central F statistic becomes important.  When the null hypothesis is
    true, the F statistic follows a central F distribution. When the null
    hypothesis is not true, then it follows a non-central F statistic.

    References
    ----------
    .. [1] Weisstein, Eric W. "Noncentral F-Distribution."
           From MathWorld--A Wolfram Web Resource.
           http://mathworld.wolfram.com/NoncentralF-Distribution.html
    .. [2] Wikipedia, "Noncentral F-distribution",
           http://en.wikipedia.org/wiki/Noncentral_F-distribution

    Examples
    --------
    In a study, testing for a specific alternative to the null hypothesis
    requires use of the Noncentral F distribution. We need to calculate the
    area in the tail of the distribution that exceeds the value of the F
    distribution for the null hypothesis.  We'll plot the two probability
    distributions for comparison.

    >>> import mars.tensor as mt
    >>> import matplotlib.pyplot as plt

    >>> dfnum = 3 # between group deg of freedom
    >>> dfden = 20 # within groups degrees of freedom
    >>> nonc = 3.0
    >>> nc_vals = mt.random.noncentral_f(dfnum, dfden, nonc, 1000000)
    >>> NF = np.histogram(nc_vals.execute(), bins=50, normed=True)  # TODO(jisheng): implement mt.histogram
    >>> c_vals = mt.random.f(dfnum, dfden, 1000000)
    >>> F = np.histogram(c_vals.execute(), bins=50, normed=True)
    >>> plt.plot(F[1][1:], F[0])
    >>> plt.plot(NF[1][1:], NF[0])
    >>> plt.show()
    """
    if 'dtype' not in kw:
        kw['dtype'] = np.random.RandomState().noncentral_f(
            handle_array(dfnum), handle_array(dfden), handle_array(nonc), size=(0,)).dtype
    size = random_state._handle_size(size)
    op = TensorNoncentralF(size=size, state=random_state._state, gpu=gpu, **kw)
    return op(dfnum, dfden, nonc, chunks=chunks)
