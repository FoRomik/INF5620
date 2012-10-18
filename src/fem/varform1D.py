"""
Solution of 1D differential equation by linear combination of
basis functions in function spaces and a variational formulation
of the differential equation problem.
"""
import sympy as sm
from scitools.std import plot, hold, legend, savefig, linspace, \
     title, xlabel, axis


def solve(integrand_lhs, integrand_rhs, phi, Omega,
          boundary_lhs=None, boundary_rhs=None,
          numint=False, verbose=False):
    """
    phi: dictionary of lists, phi[0] holdes the basis functions,
    phi[1] holdes the first-order derivatives, and phi[2] the
    second-order derivatives (and so on).
    integrand_lhs and integrand_rhs are functions of phi
    defining the integrands in integrals over Omega in the variational
    formulation. boundary_lhs/rhs are similar functions defining
    contributions from the boundary (boundary integrals, which are point
    values in 1D).

    if numint True, all integrals are calculated by sympy.mpmath.quad
    to high precision.
    if verbose is True, integrations and linear system A*c=b are printed
    during the computations.
    """
    N = len(phi[0]) - 1
    A = sm.zeros((N+1, N+1))
    b = sm.zeros((N+1, 1))
    x = sm.Symbol('x')
    print '...evaluating matrix...',
    for i in range(N+1):
        for j in range(i, N+1):
            integrand = integrand_lhs(phi, i, j)
            if verbose:
                print '(%d,%d):' % (i, j), integrand
            if not numint:
                I = sm.integrate(integrand, (x, Omega[0], Omega[1]))
                if isinstance(I, sm.Integral):
                    numint = True  # force numerical integration hereafter
                    print 'numerical integration of', integrand
            if numint:
                integrand_ = sm.lambdify([x], integrand)
                try:
                    I = sm.mpmath.quad(integrand_, [Omega[0], Omega[1]])
                except NameError, e:
                    raise NameError('Numerical integration of\n%s\nrequires symbol %s to be given a value' %
                                    (integrand, str(e).split()[2]))
            if boundary_lhs is not None:
                I += boundary_lhs(phi, i, j)
            A[i,j] = A[j,i] = I
        integrand = integrand_rhs(phi, i)
        if verbose:
            print 'rhs:', integrand
        if not numint:
            I = sm.integrate(integrand, (x, Omega[0], Omega[1]))
            if isinstance(I, sm.Integral):
                numint = True
                print 'numerical integration of', integrand
        if numint:
            integrand_ = sm.lambdify([x], integrand)
            try:
                I = sm.mpmath.quad(integrand_, [Omega[0], Omega[1]])
            except NameError, e:
                raise NameError('Numerical integration of\n%s\nrequires symbol %s to be given a value' %
                                (integrand, str(e).split()[2]))
        if boundary_rhs is not None:
            I += boundary_rhs(phi, i)
        b[i,0] = I
    print
    if verbose: print 'A:\n', A, '\nb:\n', b
    c = A.LUsolve(b)
    #c = sm.mpmath.lu_solve(A, b)
    if verbose: print 'coeff:', c
    u = 0
    for i in range(len(phi[0])):
        u += c[i,0]*phi[0][i]
    if verbose: print 'approximation:', u
    return u
    
def collocation(term_lhs, term_rhs, phi, points):
    """
    Solve a differential equation by collocation. term_lhs is
    a function of phi (dict of basis functions and their derivatives)
    and points (the collocation points throughout the domain)
    as well as i and j (the matrix index) returning elements in the
    coefficient matrix, while term_rhs is a function of phi, i and
    points returning the element i in the right-hand side vector.
    Note that the given phi is transformed to Python functions through
    sm.lambdify such that term_lhs and term_rhs can simply evaluate
    phi[0][i], ... at a point.
    """
    N = len(phi[0]) - 1
    A = sm.zeros((N+1, N+1))
    b = sm.zeros((N+1, 1))
    # Wrap phi in Python functions (phi_) rather than expressions
    # so that we can evaluate phi_ at points[i] (alternative to subs?)
    x = sm.Symbol('x')
    phi_ = {}
    module = "numpy" if N > 2 else "sympy" 
    for derivative in phi:
        phi_[derivative] = [sm.lambdify([x], phi[derivative][i],
                                        modules="sympy")
                            for i in range(N+1)]
    print '...evaluating matrix...',
    for i in range(N+1):
        for j in range(N+1):
            print '(%d,%d)' % (i, j)
            A[i,j] = term_lhs(phi_, points, i, j)
        b[i,0] = term_rhs(phi_, points, i)
    print

    # Drop symbolic expressions (and symbolic solve) for
    # all but the smallest problems (troubles maybe caused by
    # derivatives of phi that trigger full symbolic expressions
    # in A; this problem is not evident in interpolation in approx1D.py)
    if N > 2:
        A = A.evalf()
        b = b.evalf()
    print 'A:\n', A, '\nb:\n', b
    c = A.LUsolve(b)
    print 'coeff:', c
    u = 0
    for i in range(len(phi_[0])):
        u += c[i,0]*phi_[0][i](x)
    print 'approximation:', u
    return u
    
def comparison_plot(u, Omega, u_e=None, filename='tmp.eps',
                    plot_title='', ymin=None, ymax=None):
    x = sm.Symbol('x')
    u = sm.lambdify([x], u, modules="numpy")
    if len(Omega) != 2:
        raise ValueError('Omega=%s must be an interval (2-list)' % str(Omega))
    # When doing symbolics, Omega can easily contain symbolic expressions,
    # assume .evalf() will work in that case to obtain numerical
    # expressions, which then must be converted to float before calling
    # linspace below
    if not isinstance(Omega[0], (int,float)):
        Omega[0] = float(Omega[0].evalf())
    if not isinstance(Omega[1], (int,float)):
        Omega[1] = float(Omega[1].evalf())
        
    resolution = 401  # no of points in plot
    xcoor = linspace(Omega[0], Omega[1], resolution)
    # Vectorized functions expressions does not work with
    # lambdify'ed functions without the modules="numpy"
    approx = u(xcoor)
    plot(xcoor, approx)
    legends = ['approximation']
    if u_e is not None:
        exact  = u_e(xcoor)
        hold('on')
        plot(xcoor, exact)
        legends = ['exact']
    legend(legends)
    title(plot_title)
    xlabel('x')
    if ymin is not None and ymax is not None:
        axis([xcoor[0], xcoor[-1], ymin, ymax])
    savefig(filename)

if __name__ == '__main__':
    print 'Module file not meant for execution.'
    

