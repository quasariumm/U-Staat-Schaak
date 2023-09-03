import os

class White():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wkn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wkr.svg"
            self.value = 0
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Queen():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wqn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wqr.svg"
            self.value = 9
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Bishop():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wbn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wbr.svg"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Knight():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wnn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wnr.svg"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wrn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wrr.svg"
            self.value = 5
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value
    
    class Pawn():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wpn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\wpr.svg"
            self.value = 1
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

class Black():
    class King():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bkn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bkr.svg"
            self.value = 0
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Queen():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bqn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bqr.svg"
            self.value = 9
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Bishop():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bbn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bbr.svg"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Knight():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bnn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bnr.svg"
            self.value = 3
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value

    class Rook():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\brn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\brr.svg"
            self.value = 5
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value
    
    class Pawn():
        def __init__(self) -> None:
            self.imgPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bpn.svg"
            self.imgRevPath = os.path.dirname(__file__) + "\\data\\img\\pieces\\Default\\bpr.svg"
            self.value = 1
            self.movement = []
        
        def __add__(self, other):
            return self.value + other.value