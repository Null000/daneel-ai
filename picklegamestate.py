import cPickle

class GameState:
	
	# g = GameState(11,22,3,4,5) init
	# g.pickle('test.gamestate') save
	# x = GameState().unpickle('test.gamestate') load		

	def __init__(self,rulesfile=None,turns=None,connection=None,
	cache=None,verbosity=None, pickle_location=None):
		if pickle_location is None:
			self.rulesfile = rulesfile
			self.turns = turns
			self.connection = connection
			self.cache = cache
			self.verbosity = verbosity
		
	def pickle(self, file_name):
		file = open(file_name, 'wb')
		cPickle.dump(self, file)
		file.close()
		return
	
	def unpickle(self, pickle_location):
		file = open(pickle_location, 'rb')
		old = cPickle.load(file)
		file.close()
		return old

		
