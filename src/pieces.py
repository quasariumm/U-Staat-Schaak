import os

class White():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wkn.png")
            self.value = 0
            self.movement = [
                [(-2,0), (-4,0)], # Castle Queenside
                [(2,0), (3,0)], # Castle Kingside
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wqn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wbn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wnn.png")
            self.value = 3
            self.movement = [
                [(-1,2)],
                [(1,2)],
                [(2,-1)],
                [(2,1)],
                [(-1,-2)],
                [(1,-2)],
                [(-2,-1)],
                [(-2,1)]
            ]
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wrn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "wpn.png")
            self.value = 1
            self.movement = [
                [(0,2)], # First move
                [(0,1)], # Normal
                [(1,1)], # Capture right
                [(-1,1)] # Capture left
            ]
        
        def __add__(self, other):
            return self.value + other.value

class Black():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "bkn.png")
            self.value = 0
            self.movement = [
                [(-2,0), (-4,0)], # Castle Queenside
                [(2,0), (3,0)], # Castle Kingside
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "bqn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "bbn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "bnn.png")
            self.value = 3
            self.movement = [
                [(-1,2)],
                [(1,2)],
                [(2,-1)],
                [(2,1)],
                [(-1,-2)],
                [(1,-2)],
                [(-2,-1)],
                [(-2,1)]
            ]
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "brn.png")
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
            self.imgPath = os.path.join(os.path.dirname(__file__), '..', 'data', 'img', 'pieces', '{}', "bpn.png")
            self.value = 1
            self.movement = [
                [(0,-2)], # First move
                [(0,-1)], # Normal
                [(1,-1)], # Capture right
                [(-1,-1)] # Capture left
            ]
        
        def __add__(self, other):
            return self.value + other.value