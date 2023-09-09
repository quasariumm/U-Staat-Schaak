import os

class White():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wkn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wkr.png"
            self.value = 0
            self.movement = [
                [(-1,0)],
                [(-1,1)],
                [(0,1)],
                [(1,1)],
                [(1,0)],
                [(1,-1)],
                [(0,-1)],
                [(-1,-1)]
            ]
        
        def __add__(self, other):
            return self.value + other.value

    class Queen():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wqn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wqr.png"
            self.value = 9
            self.movement = [
                [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0)],
                [(-1,0),(-2,0),(-3,0),(-4,0),(-5,0),(-6,0),(-7,0)],
                [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7)],
                [(0,-1),(0,-2),(0,-3),(0,-4),(0,-5),(0,-6),(0,-7)],
                [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)],
                [(-1,-1),(-2,-2),(-3,-3),(-4,-4),(-5,-5),(-6,-6),(-7,-7)],
                [(1,-1),(2,-2),(3,-3),(4,-4),(5,-5),(6,-6),(7,-7)],
                [(-1,1),(-2,2),(-3,3),(-4,4),(-5,5),(-6,6),(-7,7)]
            ]
        
        def __add__(self, other):
            return self.value + other.value

    class Bishop():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wbn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wbr.png"
            self.value = 3
            self.movement = [
                [(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)],
                [(-1,-1),(-2,-2),(-3,-3),(-4,-4),(-5,-5),(-6,-6),(-7,-7)],
                [(1,-1),(2,-2),(3,-3),(4,-4),(5,-5),(6,-6),(7,-7)],
                [(-1,1),(-2,2),(-3,3),(-4,4),(-5,5),(-6,6),(-7,7)]
            ]
        
        def __add__(self, other):
            return self.value + other.value

    class Knight():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wnn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wnr.png"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wrn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wrr.png"
            self.value = 5
            self.movement = [
                [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0)],
                [(-1,0),(-2,0),(-3,0),(-4,0),(-5,0),(-6,0),(-7,0)],
                [(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7)],
                [(0,-1),(0,-2),(0,-3),(0,-4),(0,-5),(0,-6),(0,-7)]
            ]
        
        def __add__(self, other):
            return self.value + other.value
    
    class Pawn():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wpn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wpr.png"
            self.value = 1
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

class Black():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bkn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bkr.png"
            self.value = 0
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Queen():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bqn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bqr.png"
            self.value = 9
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Bishop():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bbn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bbr.png"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Knight():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bnn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bnr.png"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\brn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\brr.png"
            self.value = 5
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value
    
    class Pawn():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bpn.png"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bpr.png"
            self.value = 1
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value