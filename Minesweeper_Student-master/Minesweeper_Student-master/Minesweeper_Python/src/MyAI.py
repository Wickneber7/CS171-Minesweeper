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
import time

import heapq


# import numpy as np # not sure if this is on the openlab env, but will be able to do some of the matrix stuff faster

class MyAI(AI):

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
        self.startX = startX
        self.startY = startY

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
        # This seems unnecessary if we drain all of the moves before doing any thinking

        self.board = list()
        for i in range(self.row):
            self.board.append([-1 for j in range(self.col)])

        self.mines = set()

        # figure out the board storage, since only reading and writing to board,
        # list vs array might be negligible in terms of speed

        self.effectiveBoard = list()
        for i in range(self.row):
            self.effectiveBoard.append([False for j in range(self.col)])
            # this board will store the effective number of bombs next to a tile?
            # can this just be the same as the regular board attribute?
            # Use None as default value for effective mines.  Update to either a positive
            # or negative value when a square is uncovered or a mine is found

        self.uncoveredBoard = list()
        for i in range(self.row):
            self.uncoveredBoard.append([0 for j in range(self.col)])
        # this board should keep track of the number of neighbors a given cell has
        # uncovered/known dangerous next to it.  This should be useful in determining
        # which cells should be processed/thought about first
        # What value should a cell have it is uncovered? or does it not matter

        self.remainingBoard = list()
        for i in range(self.row):
            self.remainingBoard.append([])
            for j in range(self.col):
                self.remainingBoard[i].append(8)
                if (i == 0 or i == self.row - 1) and (j == 0 or j == self.col - 1):
                    self.remainingBoard[i][j] -= 5
                elif (i == 0 or i == self.row - 1) or (j == 0 or j == self.col - 1):
                    self.remainingBoard[i][j] -= 3

        # Not sure if need this, but easier to think about with it instead of doubling
        # the purpose of the uncovered board.

        self.expanded_set = set()
        self.future_expansion = set()
        # This set holds onto tiles that have been expanded (neighbors uncovered).  0's should
        # be put into this set pretty much right away.  Tiles that become 0, should be put into
        # this as soon as possible?


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

        # Should this even be here?  Trying to remember why this was here, think it had something
        # to do with the first move being problematic
        #self.board[self.lastX][self.lastY] = 0
        #self.explored.add((self.lastX, self.lastY))

        #self.remSquares -= 1 # This was causing problems, I think I was double adding

        #self.effectiveBoard[self.lastX][self.lastY] = 0
        # if ( len(self.move_set) > 0):
        self.flag_set = set()

        # __init__ supposed to all get action for the first move, or will that
        # happen automatically?

    ########################################################################
    #							YOUR CODE ENDS
    ########################################################################

    def _updateEffective(self, row, col):
        for i in range(row - 1, row + 2, 1):
            for j in range(col - 1, col + 2, 1):
                if ((i >= self.row or i < 0) or (j >= self.col or j < 0)):
                    pass
                else:
                    # Effective shouldn't go negative, not that would
                    # be a problem?
                    self.effectiveBoard[i][j] -= 1

    def _generateSurrounding(self, row, col) -> [(int, int)]:
        ret_list = list()
        for i in range(row - 1, row + 2, 1):
            for j in range(col - 1, col + 2, 1):
                if ((i >= self.row or i < 0) or (j >= self.col or j < 0) or (i == row and j == col)):
                    pass
                else:
                    ret_list.append((i, j))

        return ret_list

    # Maybe condense all of the increment, decrement and stuff on surroundings into 1
    # fucntion
    def _actOnSurrounging(self, row, col, board, action) -> [[]]:
        pass

    def getAction(self, number: int) -> "Action Object":

        '''
        Order of operation
        1 Save the returned square to the board and update all other boards
        2 Check if there is more work to do, or if game is complete
        3 Update neighbor cells (0 easy, non 0 less easy, need to think about)
        4 Main actual AI logic
        '''
        '''
        when uncovering neighbors of 0s, should we begin processing and thinking
        about where the mines are, or should we just uncover all known safe squares
        then begin our thinking

        if a square has effective number == number of not unncovered neighbor
        squares, then the uncovered square is a mine.  That square becomes an
        effective 0 and its neighbors that are not uncovered or mines should be
        put into the safe list
        '''
        ########################################################################
        #							YOUR CODE BEGINS						   #
        ########################################################################

        # Update our board, add the cell to explored, and decrement number of cells
        print(self.explored)

        self.board[self.lastX][self.lastY] = number
        self.explored.add((self.lastX, self.lastY))
        self.remSquares -= 1

        if self.effectiveBoard[self.lastX][self.lastY] is False:
            self.effectiveBoard[self.lastX][self.lastY] = number
        else:
            self.effectiveBoard[self.lastX][self.lastY] += number

        print(self.lastX,self.lastY)

        # for the neighbors of returned cell, increment the number uncovered cells nearby
        # Need to change this to decrement if decide to keep track of cells not uncovered

        for i, j in self._generateSurrounding(self.lastX, self.lastY):
            self.uncoveredBoard[i][j] += 1
            self.remainingBoard[i][j] -= 1

        print("Remaining Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(self.remainingBoard[j][i]) + "\t", end='')
            print()

        # Need to adjust the new square's effective mine number, since may already
        # know where all of the neighboring mines are when a square is uncovered
        # What's the effective number of mines for a square that has yet to be uncovered?
        # If default it to 0, would need to do an additional check on the processing
        # but also allows quick effective + real once the square is uncovered
        if self.remSquares - self.remMines == 0:
            return Action(AI.Action.LEAVE)
        if number == 0:
            '''
            If a cell returns 0, then the 8 adjacent squares are safe.  These
            squares should be added to the move_queue if they have not been
            explored.  Should then update the neighborsBoard and the regular board
            '''
            self.board[self.lastX][self.lastY] = 0
            self.expanded_set.add((self.lastX,self.lastY))
            for i in range(self.lastX - 1, self.lastX + 2, 1):
                for j in range(self.lastY - 1, self.lastY + 2, 1):
                    if (i >= self.row or i < 0) or (j >= self.col or j < 0):
                        pass
                    elif (i, j) not in self.explored:
                        self.safe.add((i, j))
                        self.move_set.add((i, j))

        if len(self.move_set) > 0:
            self.lastX, self.lastY = self.move_set.pop()
            print(self.lastX, self.lastY)
            return Action(AI.Action.UNCOVER, self.lastX,
                          self.lastY)  # adjust this to be the correct action type
            # else # don't need the else I think

            # How do we figure out which cell's to check for the
            # nested for loop kinda sucks, but its also techincally O(n) for this
            # type of problem since we define n as row*col

            # What's the order of checking, check squares with available squares =
            # effective number of mines
            # How do we know which of the squares are not in use?
            # Maybe store the relative direction of squares that are available
            # Would that even give significant speed up over just scanning
        print("Effective Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(self.effectiveBoard[j][i]) + "\t", end='')
            print()
        print("Remaining Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(self.remainingBoard[j][i]) + "\t", end='')
            print()

        for i in range(self.row):
            for j in range(self.col):
                # Scan every board slot, if the remaining covered squares = the effective mines
                # then the remaining squares must be mines
                if self.remainingBoard[i][j] == self.effectiveBoard[i][j] and self.effectiveBoard != 0:
                    print("scanning for", i, j)
                    scan_list = self._generateSurrounding(i, j)
                    # Find out what the remaining squares actually are, (will have board value -1)

                    for r, c in scan_list:
                        if self.board[r][c] == -1 and (r,c) not in self.mines:
                            self.mines.add((r, c))
                            update_list = self._generateSurrounding(r, c)

                            # This might not be working as intended
                            print(update_list)
                            for n, m in update_list:
                                #print("Before", self.remainingBoard[n][m])
                                if self.effectiveBoard[n][m] is False:
                                    self.effectiveBoard[n][m] = 0
                                self.effectiveBoard[n][m] -= 1
                                self.remainingBoard[n][m] -= 1
                                self.uncoveredBoard[n][m] += 1

                                # Maybe I can just move the move set addition and remove this
                                if self.effectiveBoard[n][m] == 0 and (n,m) not in self.expanded_set:
                                    print("adding to future expansion")
                                    self.future_expansion.add((n,m))

                                #print("After",self.remainingBoard[n][m])

        print("Mine set")
        print(self.mines)

        # Thinking about it, not sure if this will actually find anything new to expand
        for i in range(self.row):
            for j in range(self.col):
                #print(i,j,self.effectiveBoard[i][j] is not False)
                #print(i,j,self.effectiveBoard[i][j] == 0)
                #print(self.effectiveBoard[i][j])
                if self.effectiveBoard[i][j] is not False and self.effectiveBoard[i][j] == 0:
                    #print("checking if", i, j, "in explored set")
                    if (i, j) not in self.explored:
                        self.move_set.add((i, j))
        print("Move set")
        print(self.move_set)
        while len(self.future_expansion) != 0:
            r,c = self.future_expansion.pop()
            scan_list = self._generateSurrounding(r,c)
            for i,j in scan_list:
                if (i,j) not in self.explored and (i,j) not in self.mines:

                    self.move_set.add((i,j))



        print("Move set")
        print(self.move_set)

        if len(self.move_set) > 0:
            self.lastX, self.lastY = self.move_set.pop()
            return Action(AI.Action.UNCOVER, self.lastX, self.lastY)
        elif len(self.flag_set) > 0:
            self.lastX, self.lastY = self.flag_set.pop()
            return Action(AI.Action.FLAG, self.lastX, self.lastY)
        else:
            print("Failed to find a move")
            print("Board State")
            for i in range(self.row - 1, -1, -1):
                for j in range(self.col):
                    print(str(self.board[j][i]) + "\t", end='')
                print()
            print("Effective Board")
            for i in range(self.row - 1, -1, -1):
                for j in range(self.col):
                    print(str(self.effectiveBoard[j][i]) + "\t", end='')
                print()
            print("Remaining Board")
            for i in range(self.row - 1, -1, -1):
                for j in range(self.col):
                    print(str(self.remainingBoard[j][i]) + "\t", end='')
                print()
            return None
            # Guessing time

    ########################################################################
    #							YOUR CODE ENDS							   #
    ########################################################################
