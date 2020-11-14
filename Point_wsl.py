from multipledispatch import dispatch

class Point:

	def __iter__(self):
		return iter((self.y,self.x))

	@dispatch()
	def __init__(self):
		self.__init__(None)

	@dispatch((int, type(None)), (int, type(None)))
	def __init__(self, y = None,x = None):
		self.y = y
		self.x = x

	@dispatch((int, type(None)))
	def __init__(self, yx = None):
		self.__init__(yx,yx)

	@dispatch(object)
	def __init__(self, p: "Point") -> "Point":
		self.y, self.x = p.copy()

	@dispatch((tuple,list))
	def __init__(self, i):
		self.y, self.x = Point(*i[:2])

	def copy(self):
		y,x = self
		return Point(y,x)

	def __eq__(self, p: "Point"):
		return (self.y == p.y) and (self.x == p.x)

	def __add__(self, arg):
		if type(arg) is type(None):
			raise TypeError("NoneType not supported for addition.")

		elif type(arg) is int:
			p = Point(arg)
			return Point(self.y + p.y, self.x + p.x)

		elif isinstance(arg, Point):
			p = arg
			return Point(self.y + p.y, self.x + p.x)

	def __radd__(self, arg):
		return self.__add__(arg)
	
	def __sub__(self, arg):
		if type(arg) is type(None):
			raise TypeError("NoneType not supported for subtraction.")

		elif type(arg) is int:
			p = Point(arg)
			return Point(self.y - p.y, self.x - p.x)

		elif isinstance(arg, Point):
			p = arg
			return Point(self.y - p.y, self.x - p.x)

	def __rsub__(self, arg):
		p = self.__sub__(arg)
		return Point(-p.y, -p.x)

	def __lt__(self, num: int):
		p = Point(num)
		return (self.y < p.y) or (self.x < p.x)

	def assign_if_none(self, p: "Point") -> "Point":
		new = Point()
		new.y = p.y if self.y is None else self.y
		new.x = p.x if self.x is None else self.x

		return new
	
	def __repr__(self):
		return "(y={}, x={})".format(self.y,self.x)

