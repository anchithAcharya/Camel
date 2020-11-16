class Stack_pointer:
	max_limit = 30

	def __init__(self) -> None:
		self._stack = []
		self._pointer = -1

	def append(self, item):
		if self._stack:
			if self._pointer != len(self._stack) - 1:
				self._stack = self._stack[:self._pointer + 1]
			
			if self._stack[-1] == item:
				return

			if len(self._stack) >= Stack_pointer.max_limit:
				self._stack.pop(0)
				self._pointer -= 1
		
		self._stack.append(item)
		self._pointer += 1
	
	def up(self):
		if self._pointer > 0:
			self._pointer -= 1
		
			return self._stack[self._pointer]

	def down(self):
		if self._pointer < len(self._stack) - 1:
			self._pointer += 1

			return self._stack[self._pointer]
	
	def get_cur(self):
		return self._stack[self._pointer]
