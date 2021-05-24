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
import random
# import random # do we need to import these ourselves
import time

import heapq
import itertools
from itertools import combinations


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

        self.remaining_moves = set()

        ###############   Stuf to think about more   ##########################

        # need to figure out the time stuff, just have a timer attribute
        # then start a timer at the beginning of every method then stop right
        # before the return and add the timer?

        # have an check in getAction, if timer > some number then switch to a
        # faster execution behaviour or just guess from there?

        # Should this even be here?  Trying to remember why this was here, think it had something
        # to do with the first move being problematic
        # self.board[self.lastX][self.lastY] = 0
        # self.explored.add((self.lastX, self.lastY))

        # self.remSquares -= 1 # This was causing problems, I think I was double adding

        # self.effectiveBoard[self.lastX][self.lastY] = 0
        # if ( len(self.move_set) > 0):
        self.flag_set = set()
        #print("New World")
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
        '''
        print("START OF MOVE")
        print("Index Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(i) + " " + str(j) + "\t", end='')
            print()
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
        '''



        self.board[self.lastX][self.lastY] = number
        self.explored.add((self.lastX, self.lastY))
        self.remSquares -= 1


        #print("moves", self.move_set)
        #print("mines", self.mines, "numMines=", len(self.mines))
        #print("remaining mines should equal", self.totalMines, "-", len(self.mines), "=", self.remMines)
        #print("Remaining squares=", self.remSquares)



        if self.effectiveBoard[self.lastX][self.lastY] is False:
            self.effectiveBoard[self.lastX][self.lastY] = number
        else:
            self.effectiveBoard[self.lastX][self.lastY] += number

        # for the neighbors of returned cell, increment the number uncovered cells nearby
        # Need to change this to decrement if decide to keep track of cells not uncovered

        for i, j in self._generateSurrounding(self.lastX, self.lastY):
            self.uncoveredBoard[i][j] += 1
            self.remainingBoard[i][j] -= 1

        # Need to adjust the new square's effective mine number, since may already
        # know where all of the neighboring mines are when a square is uncovered
        # What's the effective number of mines for a square that has yet to be uncovered?
        # If default it to 0, would need to do an additional check on the processing
        # but also allows quick effective + real once the square is uncovered

        # This might need to be just regular numMines
        if self.remSquares - self.totalMines == 0:
            return Action(AI.Action.LEAVE)




        # This feels a little hacky but maybe it's alright
        if self.remMines == 0:
            for i in range(self.row):
                for j in range(self.col):
                    if (i,j) not in self.explored and (i,j) not in self.mines:
                        self.move_set.add((i,j))


        if number == 0:
            '''
            If a cell returns 0, then the 8 adjacent squares are safe.  These
            squares should be added to the move_queue if they have not been
            explored.  Should then update the neighborsBoard and the regular board
            '''
            self.board[self.lastX][self.lastY] = 0
            self.expanded_set.add((self.lastX, self.lastY))
            for i in range(self.lastX - 1, self.lastX + 2, 1):
                for j in range(self.lastY - 1, self.lastY + 2, 1):
                    if (i >= self.row or i < 0) or (j >= self.col or j < 0):
                        pass
                    elif (i, j) not in self.explored:
                        self.safe.add((i, j))
                        self.move_set.add((i, j))

        if len(self.move_set) > 0:
            self.lastX, self.lastY = self.move_set.pop()
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

        for i in range(self.row):
            for j in range(self.col):
                # Scan every board slot, if the remaining covered squares = the effective mines
                # then the remaining squares must be mines
                if self.remainingBoard[i][j] == self.effectiveBoard[i][j] and self.effectiveBoard != 0:
                    scan_list = self._generateSurrounding(i, j)
                    # Find out what the remaining squares actually are, (will have board value -1)

                    for r, c in scan_list:
                        if self.board[r][c] == -1 and (r, c) not in self.mines:
                            self.mines.add((r, c))
                            self.remMines -= 1
                            update_list = self._generateSurrounding(r, c)
                            # This might not be working as intended
                            for n, m in update_list:
                                if self.effectiveBoard[n][m] is False:
                                    self.effectiveBoard[n][m] = 0
                                self.effectiveBoard[n][m] -= 1
                                self.remainingBoard[n][m] -= 1
                                self.uncoveredBoard[n][m] += 1

                                # Maybe I can just move the move set addition and remove this
                                # Instead of having the while loop down below, maybe just do that work here
                                # or does this prevent double adding/double work
                                if self.effectiveBoard[n][m] == 0 and (n, m) not in self.expanded_set:
                                    self.future_expansion.add((n, m))

        # Thinking about it, not sure if this will actually find anything new to expand
        # Probably delete if time is tight, not sure if this is doing anything
        for i in range(self.row):
            for j in range(self.col):
                if self.effectiveBoard[i][j] is not False and self.effectiveBoard[i][j] == 0:
                    if (i, j) not in self.explored:
                        self.move_set.add((i, j))
                    # Maybe this should stay in the if, not sure if will have ever a new thing to add with this
                    surrounding = self._generateSurrounding(i,j)
                    for r,c in surrounding:
                        if (r,c) not in self.explored and (r,c) not in self.mines:
                            self.move_set.add((r,c))


        while len(self.future_expansion) != 0:
            r, c = self.future_expansion.pop()
            scan_list = self._generateSurrounding(r, c)
            for i, j in scan_list:
                if (i, j) not in self.explored and (i, j) not in self.mines:
                    self.move_set.add((i, j))

        # We should also be able to do this check before/earlier and not have to make a loop for it
        # This should probably go earlier, but it doesn't really matter
        for i in range(self.row):
            for j in range(self.col):
                if self.remainingBoard[i][j] == 0 and ((i, j) not in self.mines and (i, j) not in self.explored):
                    self.move_set.add((i, j))

        if len(self.move_set) > 0:
            self.lastX, self.lastY = self.move_set.pop()
            return Action(AI.Action.UNCOVER, self.lastX, self.lastY)
        elif len(self.flag_set) > 0:
            self.lastX, self.lastY = self.flag_set.pop()
            return Action(AI.Action.FLAG, self.lastX, self.lastY)
        else:

            #self.lastX = random.randint(0, self.row)
            #self.lastY = random.randint(0, self.col)


            self.getCSPAction()

            for i in range(self.row):
                for j in range(self.col):
                    if self.effectiveBoard[i][j] is not False and self.effectiveBoard[i][j] == 0:
                        if (i, j) not in self.explored:
                            self.move_set.add((i, j))
                        surrounding = self._generateSurrounding(i, j)
                        for r, c in surrounding:
                            if (r, c) not in self.explored and (r, c) not in self.mines:
                                self.move_set.add((r, c))

            if len(self.move_set) > 0:
                #print(self.move_set)
                self.lastX, self.lastY = self.move_set.pop()
                return Action(AI.Action.UNCOVER, self.lastX, self.lastY)



            #print("Had to guess")

            '''
            if num frontiers == num mines, then we can guess every tile thats not in the frontiers since there 
            must be at least 1 mine in each frontier
            
            '''
            if len(self.mines) > 0:
                #print(self.mines, "=============")

                self.lastX, self.lastY = self.mines.pop()
                self.mines.add((self.lastX, self.lastY))
            else:
                #print("No mines to guess from==============")
                while (self.lastX, self.lastY) not in self.mines and (self.lastX, self.lastY) not in self.explored:
                    self.lastX = random.randint(0, self.row)
                    self.lastY = random.randint(0, self.col)

                return Action(AI.Action.UNCOVER, self.lastX, self.lastY)
            '''
            print("Index Board")
            for i in range(self.row - 1, -1, -1):
                for j in range(self.col):
                    print(str(i) + " " + str(j) + "\t", end='')
                print()
            print("Effective Board")
            for i in range(self.row - 1, -1, -1):
                for j in range(self.col):
                    print(str(self.effectiveBoard[j][i]) + "\t", end='')
                print()
            '''
            return Action(AI.Action.UNCOVER, self.lastX,
                          self.lastY)
            # return self.getCSPAction()

    def _getNeighborIndices(self, row, col):
        return [(row + 1, col), (row - 1, col), (row, col + 1), (row, col - 1)]

    def _edgeCheck(self, row, col):
        return (row == 0 or col == 0) or (row == self.row - 1 or col == self.col - 1)

    def _cornerCheck(self, row, col):
        return (row == 0 or row == self.row - 1) and (col == 0 or col == self.col - 1)

    def getCSPAction(self):
        '''
        1 Generate all of the frontiers
        2 Maybe order the frontiers by size or some other factor
        3 Actually do the work
            1 Map frontier tiles to numbers 0 - N
            2 Try placing 1-M mins in the frontier and check for consistency
            3 Save any known safe spaces or mine locations, ypdate surrounding tiles to mines
        '''
        '''
        Right now have 14 worlds where we thinkg we are making a safe move an are instead losing
        '''

        # These are the sets of frontiers
        redSets = []
        blueSets = []
        #print("Doing CSP stuff")

        '''
        print("Index Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(j) + " " + str(i) + "\t", end='')
            print()

        
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
        '''

        # These are the sets that contain all red and blue tiles already in a frontier
        expandedBlue = set()
        expandedRed = set()
        count = 1  #
        for i in range(self.row):
            for j in range(self.col):
                if self.effectiveBoard[i][j] is not False and self.effectiveBoard[i][j] > 0 and (
                i, j) not in expandedRed:

                    # We can create a new set for this node, since if it has not been expanded before, then it is not
                    # connected to any existing frontier
                    #print("appending", i, j)
                    redSets.append({(i, j)})
                    blueSets.append(set())

                    surroundings = self._generateSurrounding(i, j)
                    blueExpand = set()
                    redExpand = set()
                    for r, c in surroundings:
                        '''
                        For each tile in the surrounging 8 tiles, check if those tiles are blue tiles, just needs
                        to not be in mines and needs to be covered to be a blue tile
                        '''
                        if self.board[r][c] == -1 and (r, c) not in self.mines and (r, c) not in expandedBlue:
                            #print("Adding first in frontier, should be a rare occurrence to see multiple of these", r,c)
                            blueExpand.add((r, c))
                        #print(blueSets)
                        first = True

                        # This while loop might not be working as intended if there are things being added


                        while len(blueExpand) != 0: # Maybe add clause " and (r,c) not in expandedBlue"
                            expR, expC = blueExpand.pop()
                            blueSets[-1].add((expR, expC))
                            expandedBlue.add((expR, expC))
                            redExp = self._generateSurrounding(expR, expC)
                            #print("RedExp is", redExp, "based off of node", expR, expC)
                            #print(len(blueExpand))
                            for iR, iC in redExp:
                                node = (iR, iC)
                                if node not in expandedRed and self.remainingBoard[iR][iC] > 0 and self.board[iR][
                                    iC] != -1:
                                    redExpand.add(node)
                                    redSets[-1].add(node)
                                    expandedRed.add(node)
                            while len(redExpand) > 0:
                                rExpR, rExpC = redExpand.pop()
                                blueExp = self._generateSurrounding(rExpR, rExpC)
                                #print()
                                #print("Expanding blue", blueExp, "based off of red node", rExpR, rExpC)
                                for bR, bC in blueExp:
                                    if self.board[bR][bC] == -1 and (bR, bC) not in self.mines and (bR, bC) not in expandedBlue:
                                        blueExpand.add((bR, bC))


                            #print("blueExpand set", blueExpand, "has len ", len(blueExpand))
                        #print("left the while loop blueExpand set", blueExpand)

        '''
        print("RedSets")
        for i in redSets:
            print(i)
        print("BlueSets")
        for i in blueSets:
            print(i)
        '''


        '''
        At this point, the frontiers have been made
        Next steps:
        Generate the models
        Check the models -> this may require more work to be done above, since the best time to generate the constraints
        is when the model is being generated
        
        What form should the constraints look like
        dict( key=redTile, value=blueTile), but then how do we check the effective number constraints?
        "parallel" dicts, have a second dict that is
        dict( key=redTile, value=effectiveNumber) -> or maybe just read off of the effective number table
        is object creation and lookup faster than doing index search? probably not
        
        so then take the intersection of mines and the dict value and compare the length to the effective number
        
        for now, discard the worlds and just keep the relevant information which is?
        
        If a tile is safe in a consistent world, increment the tile's mapping in a dict or something
        
        Then once there are no more worlds, check if any value is equal to the number of worlds or 0
        If 0, then was safe in no worlds therefore is a mine, if equal to num worlds, then was safe in every world
        
        update the move set and the mines set accordingly -> might have some annoying upkeep stuff to also do
        with the updating of supporting boards, need to double check though
        
        Make this instead so that we are counting the number of are mines rather than the number of times are safe
        '''
        '''
        Facts about frontiers:
        1 Each frontier must have at least 1 mine, so then the maximum number of mines to be placed in a frontier is
        min(N - (M-1), k)
        where N is the remaining number of mines
              M is the number of sets in redSets
              k is the number of tiles in the frontier
        
        '''

        # This is pretty inefficient right now, but should work fine
        frontierMapping = {}
        for i in expandedRed:
            r,c = i
            frontierMapping[i] = set(self._generateSurrounding(r,c)).intersection(expandedBlue)


        #print("frontierMapping")
        #print(frontierMapping)


        '''
        The AI is noticeable slow when len(frontier) > 21 or 22, but very much especially when maxNumMines > len(frontier)/2
        only extreme cases should be fails on time, but curious about the speed of C++ compared to Python considering that
        prof said 2^20 not a big deal to outright enumerate all possibiliies, but ofc exponential growth so 2^21 is 
        significantly larger than 2^20 and so on
        
        Is brute force enumeration better? Shouldn't be?  20 tiles and 8 mines means 20 nCr 1 + 20 nCr 2 + ... + 20 nCr 8
        vs 2^20, so 20 + 190 + 1140 + 4845 + 15504 + 38760 +77520 + 125970 = 262809 which is about a quarter of 2^20
        
        This performance degrades as the maxNumMines increases, looking forward 9: 167960, 10: 184756, this means if
        maxNumMines were 20, we'd end up doing more work than straight enumeration, approx 200k more models, but 200k
        isn't necessarily significant, but this ratio worsens drastically with larger frontiers
        
        
        
        Speed up ideas
        - limit the number of mines, raise lower bound (very little gain except for large frontiers), lower the ceiling
        of the max num mines
        
        the minimum number of mines is ceil(len(frontier)/3) ? or is at least approximately that can just do something
        like ceil(len(frontier)/4) instead and instead of having to start at 1 mine, start at that number of mines
        is this really faster
        
        the max number of mines might be able to be thought of as some function of len(frontier) and distribution of 
        effective numbers?
        
        If have a high ratio of effective 3's then, will need fewer mines than if only had 1's?
        
        0 0 0 0 0
        0 X X X X
        
        Let the X's be the red tiles, and the 0's be the blue tiles
        
        Need to think about this more
        
        
        
        Already trimming mines down by saying each frontier needs at least 1 mine.  Can't necessarily say that if there
        are tiles outside of the blue and red, that they have a mine, but can be almost certain for larger boards, but
        risky to estimate this fact, but even shaving 1 or 2 mines off will be significant.
        
        
        Can try enumerating over all possible worlds, then stopping once the first consistent world is found, then 
        maxNumMines -= consistentWorldNumMines, for the OTHER frontiers.
        
        Unsure if between worlds if the num mines require to make a consistent world can drop, assuming that we only add
        red tiles and don't find any mine locations.  I think it should be fine, like the minimum shouldn't get any
        smaller with more red tiles, since more constraints would only potentially make that model invalid, which then
        means the next minimum is larger than the previously invalidated one which is not a problem.
        
        
        Is there a way to recycle worlds, adding red tiles shouldn't expand the number of legal worlds, only reduce the
        number of legal worlds, assuming the same blue frontier, or at least approximately the same blue frontier
        
        B B B B   ->    B B B B
        X X X B         X X X X
        
        The addition of the bottom red tile shouldn't create more legal worlds, only serve to reduce the number of legal
        worlds, so if we could save the legal worlds from the left, then check for consistency on the right, that might
        be good.  But what is the actual speed up on this, doesn't necessarily seem significant?  This will/might break
        if the new blue set is too small of a proper subset of the original blue set
        
        
        The function for finding a soft max number of mines might be the best idea.
        
        1 2 1 2 1 2
        X 0 X 0 X 0
        
        0 0 0 1 X
        0 0 0 2 0
        1 2 1 3 X
        X 0 X 0 X
        
        Might be able to say if number of 1's in frontier >= half, the max num mines = len(frontier/2), but maybe 
        add some constant factor just as security
        
        For times when maxNumMines approximately equals  
        '''
        t = 0
        foundMine = False
        for frontier in blueSets:

            blueMap = {key: 0 for key in blueSets[t]}

            maxNumMines = min(self.remMines - (len(blueSets) - 1), len(frontier))
            if len(frontier) > 20:
                #print(len(frontier),maxNumMines)
                self.move_set.add(self.mines.pop())
                return

            #print("maxNumMines",maxNumMines)
            numConsistent = 0
            for i in range(1, maxNumMines+1):
                #print(i)
                worlds = combinations(frontier, i)
                while True:
                    try:
                        model = next(worlds)
                        #print(model)
                        '''
                        At this point, the world has been generated so what needs to be done?
                        Verify the model is consistent -> for each value in the red set, check that the intersection
                        of its frontier mapping value and the model has the same len == effective board number
                        then in the blueTiles dict, increment the value if it is a mine (in the model)
                        '''
                        consistent = True
                        for j in redSets[t]:
                            r,c = j
                            if self.effectiveBoard[r][c] != len(frontierMapping[j].intersection(set(model))):
                                consistent = False
                                break

                        if consistent is True:
                            #print(model)
                            numConsistent += 1
                            for key in model:
                                blueMap[key] += 1
                    except StopIteration:
                        #print("No more worlds with",i,"mines")
                        break

            #print("Numbere of consistent worlds =", numConsistent)
            notAllConsistentCheck = False
            for value in blueMap.values():
                if value != 0:
                    notAllConsistentCheck = True
                    '''
                    Probably need some additional behavior here
                    '''

                    break

            if notAllConsistentCheck:
                for key, value in blueMap.items():
                    if value == 0:
                        '''
                        What happens if "every" world is consistent, ie have a board that looks like
                        ? ? ?
                        X 5 X
                        X 4 X
                        
                        Then it's just a pure chance guess, so how do we check if every k/v is consistent or not
                        Should in theory just be a small number of things, just do something like looping through the
                        values
                        '''
                        self.move_set.add(key)

                    elif value == numConsistent:
                        #print("Need to add tile", key, "to mines set")
                        foundMine = True
                        self.mines.add(key)
                        self.remMines -= 1
                        nr, nc = key
                        update_list = self._generateSurrounding(nr, nc)
                        for n, m in update_list:
                            if self.effectiveBoard[n][m] is False:
                                self.effectiveBoard[n][m] = 0
                            self.effectiveBoard[n][m] -= 1
                            self.remainingBoard[n][m] -= 1
                            self.uncoveredBoard[n][m] += 1
                            # self.move_set.add(key)
                            if self.effectiveBoard[n][m] == 0 and (n, m) not in self.expanded_set:
                                self.future_expansion.add((n, m))

            while len(self.future_expansion) != 0:
                r, c = self.future_expansion.pop()
                scan_list = self._generateSurrounding(r, c)
                for i, j in scan_list:
                    if (i, j) not in self.explored and (i, j) not in self.mines:
                        #print("Expanding off of safe node", r, c, "adding", i,j)
                        self.move_set.add((i, j))
            t += 1


            #print("blueMap")
            #print(blueMap)

        '''
        Need to adjust the code so that, if no safe square or mine is found, we resort to probabilities
        
        If safe square is found, then just exit the function and move on
        If only a mine is found, will need to rerun the function
        '''

        if foundMine is True:
            pass
            #self.getCSPAction()


