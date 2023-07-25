"""
Kolmogorov-Smirnov statistics and related utilities.
"""

import numpy as np

def ranks(data, normalize=False):
  """
  Compute the ranks for a 1-dimensional sequence `X` of i.i.d. random
  variables.

  Parameters
  ----------
  data : array_like
    Input data.
  normalize : bool, default `False`
    Whether to normalize the ranks by the total number of data points.

  Returns
  -------
  ndarray
    1-dimensional array of ranks.

  Notes
  -----
  This is essentially a simplified version of Scipy's `scipy.stats.rankdata`,
  which provides more flexibility and safety at the cost of speed. We recommend
  only using this rank implementation if you know what you're doing.
  Specifically, `data` should be a 1-dimensional sequence that can be cast to a
  Numpy n-dimensional array.

  Examples
  --------
  >>> a = [0.5, 1.0, 0.25, 0.75, 0.95, 0.245]
  >>> ranks(a)
  array([3., 6., 2., 4., 5., 1.])
  """
  X_arr = np.asarray(data)

  n = len(X_arr)
  ranks = np.empty(n, dtype=float)
  idxs = X_arr.argsort()

  ranks[idxs[:n]] = np.arange(1, n+1)

  if normalize:
    return (ranks / n)
  else:
    return ranks

def empirical_distribution(data, t):
  """
  Evaluate the empirical cumulative distribution at a certain value over a set
  of i.i.d. random variables:

  $$\hat{F}_n(t) = \frac{1}{n} \sum_{i=1}^n \mathbb{1}_{X_i \leq t}$$

  Parameters
  ----------
  data : array-like
    Data over which to compute the empirical distribution.
  t : float
    Numeric value at which to evaluate the empirical distribution function.

  Returns
  -------
  float
    Value in the range $(0.0, 1.0)$ indicating the cumulative distribution at
    `t`.

  Notes
  -----
  If $t$ is less than the minimum or greater than the maximum value of `data`,
  returns `0.0` or `1.0`, respectively.

  Examples
  --------
  >>> d = [0.5, 1.0, 0.25, 0.75, 0.95, 0.245]
  >>> t = 0.25
  >>> empirical_distribution(d, t)
  0.3333333333333333
  """
  # Cast to numpy if needed
  X = np.asarray(data)
  n = len(X)

  leq = (X <= t)
  less_sum = float(np.sum(leq))
  
  return (less_sum / n)

def ks_statistic(data, cdf = 'gaussian'):
  """
  Calculate the Kolmogorov-Smirnov statistic for a set of i.i.d. random
  variables.

  The KS statistic is defined as:

  $$D_n = \textrm{sup}_x \abs{F_n(x) - F(x)}$$

  where $\textrm{sup}_x$ is the supremum over all values of $x$, $F_n(x)$ is
  the empirical distribution at $x$ for $n$ i.i.d. random variables $X_i$, and
  $F(x)$ is a cumulative distribution function against which to perform the
  test.

  Parameters
  ----------
  data : array-like
    Data on which to perform the test.
  cdf : str or array-like
    Name of a distribution in `scipy.stats` (for testing against a theoretical
    distribution), or a second set of random variables (for testing against
    another empirical distribution).

  Returns
  -------
  float
    Kolmogorov-Smirnov statistic.

  Notes
  -----
  It is perfectly valid to use either a theoretical distribution (such as a
  standard Gaussian) for $F(x)$, or a second empirical distribution, which does
  not need to be the same length as $F_n(x)$.
  """
  raise NotImplementedError