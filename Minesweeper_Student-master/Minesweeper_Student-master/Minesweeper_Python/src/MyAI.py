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

        self.board[self.lastX][self.lastY] = number
        self.explored.add((self.lastX, self.lastY))
        self.remSquares -= 1

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
        if self.remSquares - self.remMines == 0:
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
            self.lastX = random.randint(0, self.row)
            self.lastY = random.randint(0, self.col)
            while (self.lastX, self.lastY) not in self.mines and (self.lastX, self.lastY) not in self.explored:
                self.lastX = random.randint(0, self.row)
                self.lastY = random.randint(0, self.col)

            self.getCSPAction()
            if len(self.move_set) > 0:
                #print(self.move_set)
                self.lastX, self.lastY = self.move_set.pop()
                return Action(AI.Action.UNCOVER, self.lastX, self.lastY)

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

        blueTiles = set()

        for i in range(self.row):
            for j in range(self.col):
                check = False
                if self._cornerCheck(i, j) and self.remainingBoard[i][j] < 3 and (i, j) not in self.mines:
                    check = True
                elif self._edgeCheck(i, j) and self.remainingBoard[i][j] < 5 and (i, j) not in self.mines:
                    check = True

                elif not self._cornerCheck(i, j) and not self._edgeCheck(i, j) and self.remainingBoard[i][j] < 8 and (
                i, j) not in self.mines:
                    check = True

                '''
                If check is True, then we have found a blue tile.  Initially, blueSets is an empty list of sets.  For each 
                blue tile, if the blue tile has a neighor in any of the sets in the list of set, then add the blue tile
                to that set.  If the blue tile has no neighbors in any set, create a new set for it.
                
                Are there any corner 2 tiles will be connected to each other in the future, but there isn't a present
                connection?
                Yes see board below, A is the first blue tile, B is the second blue tile, C are all other blue tiles,
                0 is a non blue tile (doesn't matter what it actually is)
                A 0 0 B
                C 0 0 C
                C C C C
                A and B will not be connected to each other when they should be
                
                What's the behavior to do instead?  Generate connected components basically
                Find all of the blue tiles and put into a set(or whatever other data structure)
                Pick a random tile, generate that tiles neighbors, pop all of the neighbors that are in the data structure
                If no neighbors in data structure, then repeat
                
                What happens if there is a case like
                0 C C C 0
                X X X X X
                0 C C C 0
                
                The X tiles represent red tiles that would constrain both regions of blue.
                How realistic is this really though?  Not very?  Is it even possible?
                Probably not, assume its not possible for now
                
                This is still problematic since this will be overly connective, instead we need to connect blue tiles
                together based on red tiles?
                
                If 2 red tiles have a blue tile in common, then those two red tiles go in the same group
                Then generate the blue groups based on the "blue" neighbors of the red tiles in each group
                
                Group red tiles into cliques, such that if A and B share a blue neighbor, together they form the 
                clique AB whose blue neighbors is the union of their individual neighbors.  Future matching can be done
                such that a single tiles is compared to a clique rather than other single tiles
                
                Can think of this as a graph
                Red tiles are Vertices Blue tiles are Edges 
                Want to find the connected components of Red tiles instead of blue tiles
                
                We can find the Vertices by looking at the edges, and a single edge shouldn't connect more than 2 vertices,
                ideally at least, would need weird situations for 3 vertices to share the same edge considering that most
                of these cases should be deducible
                
                Order of operations should be then as follows
                Determine if a tile is a blue tile (which is done above)
                Find all red tiles surrounding the blue tile and add them to a bag ( or set or maybe a dict?)
                key=red tile and value =all blue tiles?
                Then for every red tile combine it with other red tiles that share a common value
                    if using a dict, this would be pop a key and its value, iterate through the dict until there is 
                    node that has a common value, then figure out something to do with the key and union the values
                
                This might be fairly inefficient, instead of just storing the blue tiles as values, is there a way to 
                get the Red tiles in there/see the red tile results?
                This probably would have to be done at the time of construction of the dict or something
                Maybe define an edge as (blue tile, red tile) or something, how do we create these?
                Technically 8 choose 2 number of potential edges to be made,but also need to include self edges/loops
                In theory bad O(n), but technically is just constant work since there are at most 8 Red tiles around a 
                Blue tile and in practice, its will generally be significantly fewer.
                
                We can generate the edges with combination and manually adding the self edge.  Once have this structure
                just run dfs on this graph/dict
                where we
                pop a key, value from the dict
                save the key to be the start of a group, then add the values to a queue or something
                until the queue is empty, pop a key, value from the queue and add the key to the group, add the value
                to the queue and remove from the dict/ or maybe just add to a visited set ( doesn't really matter i think)
                when queue is empty start over
                
                
                Is chaining faster than this?  How to chaing?
                Pick a random red tile (scan until it's found)
                Find all of its neighbors that are blue tiles, and put them into a stack/queue
                Until the stack is empty, pop a blue tile and any any new red neighbor.
                Red neighbors should go in a set and can just do set intersection
                New red tiles go into their own stack and get popped once the blue stack is empty
                Once both stacks are empty, resume the scan, if find a new red tile, check if it is in the existing
                red sets
                
                THis might be faster/better since less overhead
                '''

                if check:
                    blueTiles.add((i, j))

                '''
                if check:
                    if len(blueSets) == 0:
                        blueSets.append({(i, j)})
                    else:
                        neighbors = self._generateSurrounding(i, j)
                        insertToOld = False
                        for l in neighbors:
                            for k in blueSets:
                                if l in k:
                                    k.add((i, j))
                                    insertToOld = True

                        if insertToOld is False:
                            blueSets.append({(i,j)})
                            redSets.append(set())
                '''
        while len(blueTiles) > 0:
            start = blueTiles.pop()

        # These are the sets of frontiers
        redSets = []
        blueSets = []

        print("Index Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(i) + " " + str(j) + "\t", end='')
            print()
        # print("Board State")
        # for i in range(self.row - 1, -1, -1):
        #    for j in range(self.col):
        #        print(str(self.board[j][i]) + "\t", end='')
        #    print()
        # print("Effective Board")
        # for i in range(self.row - 1, -1, -1):
        #    for j in range(self.col):
        #        print(str(self.effectiveBoard[j][i]) + "\t", end='')
        #    print()
        print("Remaining Board")
        for i in range(self.row - 1, -1, -1):
            for j in range(self.col):
                print(str(self.remainingBoard[j][i]) + "\t", end='')
            print()

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
                    print("appending", i, j)
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
                            print("Adding first in frontier, should be a rare occurrence to see multiple of these", r,
                                  c)
                            blueExpand.add((r, c))
                        #print(blueSets)
                        first = True
                        # This while loop might not be working as intended if there are things being added
                        while len(blueExpand) > 0: # Maybe add clause " and (r,c) not in expandedBlue"
                            #print("Entered the while loop")
                            expR, expC = blueExpand.pop()
                            blueSets[-1].add((expR, expC))
                            expandedBlue.add((expR, expC))
                            redExp = self._generateSurrounding(expR, expC)
                            for iR, iC in redExp:
                                node = (iR, iC)
                                if node not in expandedRed and self.remainingBoard[iR][iC] > 0 and self.board[iR][
                                    iC] != -1:
                                    redExpand.add(node)
                                    redSets[-1].add(node)
                                    expandedRed.add(node)
                            if len(redExpand) == 0:
                                break
                            while len(redExpand) > 0:
                                rExpR, rExpC = redExpand.pop()
                                blueExp = self._generateSurrounding(rExpR, rExpC)
                                for bR, bC in blueExp:
                                    if self.board[bR][bC] == -1 and (bR, bC) not in self.mines and (
                                    bR, bC) not in expandedBlue:
                                        blueExpand.add((bR, bC))

        print("RedSets")
        for i in redSets:
            print(i)
        print("BlueSets")
        for i in blueSets:
            print(i)
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

        t = 0
        for frontier in blueSets:
            blueMap = {key: 0 for key in blueSets[t]}

            maxNumMines = min(self.remMines - (len(blueSets) - 1), len(frontier))
            print("maxNumMines",maxNumMines)
            numConsistent = 0
            for i in range(1, maxNumMines+1):
                print(i)
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
                            numConsistent += 1
                            for key in model:
                                blueMap[key] += 1
                    except StopIteration:
                        print("No more worlds with",i,"mines")
                        break

            for key, value in blueMap.items():
                if value == 0:
                    print("Need to add move", key, "to move set")
                    '''
                    Do the proper upkeep stuff here which is what -> nothing I think
                    since we decrement remaining and increment uncovered at the start of get action
                    '''
                    self.move_set.add(key)
                elif value == numConsistent:
                    print("Need to add tile", key, "to mines set")
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
            t += 1
            print(blueMap)

