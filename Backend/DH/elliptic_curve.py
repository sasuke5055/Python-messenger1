class EllipticCurve:
    def __init__(self, a, b):
        """Representation of curve given by formula y^2 = x^3 + a*x +b"""

        self.a = a
        self.b = b
        if not self.is_smooth():
            raise Exception("Incorrect (a, b) curve needs to be smooth")

    def is_smooth(self):
        """Function check if curve is smooth (can be used in DH)"""

        return 4 * self.a**3 + 27 * self.b**2 != 0

    def lay_on_curve(self, x, y):
        """Check if point (x, y) lies on the curve"""

        return y**2 == x**3 + self.a * x + self.b

    def __str__(self):

        return "y^2 = x^3 + " + str(self.a) + "*x + " + str(self.b)

    def __eq__(self, point):
        return (self.a, self.b) == (point.a, point.b)


class CurvePoint:
    """Function represent point laying on EllipticCurve curve"""

    def __init__(self, curve, x, y):
        self.curve = curve
        self.x = x
        self.y = y

        # Check if point lay on Curve
        if not curve.lay_on_curve(x, y):
            raise Exception("Incorrect coordinates, point: (" + str(self.x) + \
                    ", " + str(self.y) +") lies outside curve: " + str(self.curve))

    def __str__(self):

        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __neg__(self):
        """Define inverse element in our Group"""
    
        return CurvePoint(self.curve, self.x, -self.y)

    def __add__(self, point):
        """Add two point from same curve.
        
        __add__ should be Group operation
        """

        # Check if points lay on the same curve
        if self.curve != point.curve:
            raise Exception("Can only add points from same curve: c1, c2 = "+ \
                    str(self.curve)+ ", "+ str(point.curve))

        # Check if point is ideal, if so then return point + 0
        if isinstance(point, IdealPoint):
            return self

        if (self.x, self.y) == (point.x, point.y):
            
            # Two vericel line cross in ideal point
            if self.y == 0:
                return IdealPoint(self.curve)

            # Special case where we cannot draw line between points
            m = (3 * self.x**2 + self.curve.a) / (2 * self.y)
        else:
            # Special case where line between points
            # don't cross curve in other point
            if self.x == point.x:
                return IdealPoint(self.curve)

            
            m = (point.y - self.y) / (point.x - self.x)

        # Find cross point
        x = m**2 - point.x - self.x
        y = m*(x - self.x) + self.y

        return CurvePoint(self.curve, x, -y)

    def __sub__(self, point):

        return self + -point

    def __mul__(self, n):
        """Compute n * Point in time O(log(n))
        
        using trick that if n loks like (1101)2
        then we can compute n * Point P as
        2^3 * P + 2^2 * P + 0 * 2^1 * P + 2^0 * P
        So we start with acc, out = P, P
        1:
        acc = acc + acc = 2^1 * P
        out = out = P
        2:
        acc = acc + acc = 2^2 * P
        out = out + acc = P + 2^2 * P
        3:
        acc = acc + acc = 2^3  * P
        out = out + acc = 2^3 * P + 2^2 * P + 2^0 * P 
        """

        P = self
        if not isinstance(n, int):
            raise Exception("n must be Integer")
        if n < 0:
            return -P * -n
        if n == 0:
            return IdealPoint(P.curve)
        # In every iteration acc is 2^i * P
        acc = P
        output = IdealPoint(self.curve)
        # Check last bit separetly to make while condition easier
        i = 1
        # Use & to make comparison faster
        if n & i == i:
            output = output + acc

        i = i << 1
        while i <= n:
            acc = acc + acc

            # Checki if i bit of n is one
            # if so add Q to output R
            if n & i == i:
                output = output + acc
            # i = i * 2, using bit shifting
            i = i << 1

        return output

    def __rmul__(self, n):

        return self * n

    def __eq__(self, point):

        if type(point) is IdealPoint:
            return False

        return (self.x, self.y) == (point.x, point.y)


class IdealPoint(CurvePoint):
    """Class represents cross point of two veritcal line
    
    Correspond to 0 in our Group
    """

    def __init__(self, curve):
        
        self.curve = curve
    
    def __str__(self):
            
        return "Ideal Point (0)"
    
    def __neg__(self):
        
        # - (IP) 0 = 0 (IP)
        return self
    
    def __add__(self, point):
        
        # (IP) 0 + P = P
        return point
    
    def __mul__(self, n):

        # (IP) 0 * n = 0 (IP)
        if not isinstance(n, int):
            raise Exception("n must be Integer")
        else:
            return self

    def __eq__(self, point):
        
        return type(point) is IdealPoint and self.curve == point.curve