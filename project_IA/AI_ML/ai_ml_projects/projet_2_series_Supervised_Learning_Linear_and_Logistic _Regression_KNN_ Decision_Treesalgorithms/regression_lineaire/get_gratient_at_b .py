def get_gradient_at_b(m,b,x,y):
    diff = 0
    N = len(x)
    for i in range (N):
        diff = diff +(y[i] - (m*x[i] +b))
    b_gradient = -2/N * diff

    return b_gradient



