# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action

# import random # do we need to import these ourselves
# import time

# import numpy as np # not sure if this is on the openlab env, but will be able to do some of the matrix stuff faster

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
                self.totalMines = totalMines
                self.remMines = totalMines
                self.row = rowDimension
                self.col = colDimension
                
                self.remSquares = rowDimension * colDimension
                # is there a reason to want to keep the hold of the original number of
                # squares, or is remaining squares sufficient
                
                self.lastX = startX
                self.lastY = startY

                self.explored = set()
                # want to keep this as a set to make checking if in quick, not sure if
                # set addition/union methods are quick though since would have to add
                # something essentially every time getAction is called

                self.safe = set()
                # maybe use this instead of explored since, if it's in this, then we can
                # assume that it has been explored and doesn't need to be readded to the
                # move queue -- think about this more, seems wrong
                
                self.board = array()
                # figure out the board storage, since only reading and writing to board,
                # list vs array might be negligible in terms of speed

                self.eBoard = array()
                # this board will store the effective number of bombs next to a tile?
                # can this just be the same as the regular board attribute?

                

                self.move_queue = list()
                # this list should only have squares that are known to be safe, will be
                # returned until empty.  Logic should put in squares until can't solve
                # anymore and then drain this queue/list -- maybe shouldn't drain right
                # away instead
                # This doesn't even need to be a list? can it be a set?  We shouldn't
                # make a move unless we know its safe (under normal behaviour)
                self.move_set = set()
                # maybe this really could be the same thing as the safe set, or maybe
                # the safe set is unnecessary?
                # If something is in the safe set, then its neighbors should have their
                # effective bomb numbers reduced already, so no point in keeping what is
                # safe and what isn't? or would keeping a safe set be useful for guessing


                ###############   Stuf to think about more   ##########################

                # need to figure out the time stuff, just have a timer attribute
                # then start a timer at the beginning of every method then stop right
                # before the return and add the timer?

                # have an check in getAction, if timer > some number then switch to a
                # faster execution behaviour or just guess from there?


                # __init__ supposed to all get action for the first move, or will that
                # happen automatically?
		
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":


                '''
                Order of operation
                1 Save the returned square to the board
                2 Check if there is more work to do, or if game is complete
                3 Update neighbor cells (0 easy, non 0 less easy, need to think about)
                4 Main actual AI logic
                '''
                '''
                when uncovering neighbors of 0s, should we begin processing and thinking
                about where the mines are, or should we just uncover all known safe squares
                then begin our thinking
                '''
		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################

                self.board[self.lastX][self.lastY] = number
                self.explored.add((lastX,lastY))
                
		if ( self.remSquares - self.remMines == 0):
                        return Action(AI.Action.LEAVE)
                if ( number == 0):
                        for i in range(self.lastX-1, self.lastX+2,1):
                                for j in range(self.lastY-1, self.lastY+2,1):
                                        if ( (i > self.row or i < 0) or (j > self.col or j < 0) ):
                                                pass
                                        elif ( (i,j) not in self.explored):
                                                self.safe.add((i,j))
                                                self.move_queue.append((i,j)) # should drop this or the set
                                                self.move_set.add((i,j))

                if ( len(self.move_set) > 0):
                        self.lastX, self.lastY = self.move_set.pop()
                        
                        return Action() # adjust this to be the correct action type
                        
                #else # don't need the else I think 
                
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

