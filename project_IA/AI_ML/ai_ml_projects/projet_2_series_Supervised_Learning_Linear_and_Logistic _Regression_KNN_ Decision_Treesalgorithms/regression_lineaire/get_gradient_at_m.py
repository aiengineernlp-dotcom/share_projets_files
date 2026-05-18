def get_gradient_at_m(m,b,x,y):
    diff = 0
    N = len(x)

    for i in range(N):
        diff += diff +(x[i] (y[i] - m*x[i]+b))
    m_gradient = -2/N * diff
    return m_gradient
