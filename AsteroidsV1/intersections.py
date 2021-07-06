import math

def intersectLines( pt1, pt2, ptA, ptB ): 

    DET_TOLERANCE = 0.00000001

    x1, y1 = pt1;   x2, y2 = pt2
    dx1 = x2 - x1;  dy1 = y2 - y1

    x, y = ptA;   xB, yB = ptB
    dx = xB - x;  dy = yB - y

    DET = (-dx1 * dy + dy1 * dx)

    if math.fabs(DET) < DET_TOLERANCE: return (0,0,0,0,0)

    DETinv = 1.0/DET

    r = DETinv * (-dy  * (x-x1) +  dx * (y-y1))

    s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))

    xi = (x1 + r*dx1 + x + s*dx)/2.0
    yi = (y1 + r*dy1 + y + s*dy)/2.0
    return ( xi, yi, 1, r, s )