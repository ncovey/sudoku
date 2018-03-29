
import sys
#import random
#import operator
import time

class SudokuPuzzle:
    ''' Utils for initializing and solving a sudoku puzzle
    '''
    def __init__(self, line:str=''):
        self.__data = []
        if (line != ''):
            if (len(line) != 81):
                raise Exception('puzzle does not have 81 elements')
            row = []
            for c in range(0, len(line)):
                if (line[c] != '.'):
                    row.append(int(line[c]))
                else:
                    row.append(0)
                if ((c+1) % 9 == 0):
                    if (len(row) != 9):
                        raise Exception('row {} does not have 9 elements'.format(row))
                    self.__data.append(row)
                    row = []
            if (len(self.__data) != 9):
                raise Exception('puzzle does not have 9 rows')

    def solved(self):
        if (not self.is_valid()):
            return False
        for row in self.__data:
            if (0 in row):
                return False
        return True

    def row(self, ridx:int):
        return self[ridx]

    def col(self, cidx:int):
        col = []
        for row in self.__data:
            col.append(row[cidx])
        return col
    
    def sector(self, row:int, col:int):
        '''
        Puzzle is divided into 3x3 "sectors" containing values 1-9. sector(0,0) is the upper left; sector(2,2) is the lower right; sector(1,1) is the center.
        '''
        row *= 3; col *= 3; sect = [];
        for r in range(row, row + 3):
            sectrow = []
            for c in range(col, col + 3):
                sectrow.append(self[r][c])
            sect.append(sectrow)
        return sect

    def get_sector_from_coord(self, x:int, y:int):
        return self.sector(int(x/3), int(y/3))

    def print(self):
        for ridx, row in enumerate(self.__data):
            r = ''
            tmprow = []
            for c in row:
                tmprow.append(str(c) if c != 0 else '.')
            r += ' {} {} {} | {} {} {} | {} {} {}'.format(tmprow[0], tmprow[1], tmprow[2], tmprow[3], tmprow[4], tmprow[5], tmprow[6], tmprow[7], tmprow[8])
            print(r)
            if (((ridx + 1) != len(self.__data)) and (ridx + 1) % 3 == 0):
                print('-------+-------+-------')

    def printsector(self, n):
        sector = self.getsector(n)
        for row in sector:
            r = ''
            for col in row:
                r += ' {} '.format(col if col != 0 else '.')
            print(r)

    def __getitem__(self, key):
        return self.__data[key]

    def get_possibilities(self):
        ''' Create a dictionary indexed by cell coordinates and a list of possible values. If a cell has a list of size 1, that cell is "solved"
            Look at puzzle and find solved cells.
            Look at all rows and remove solved cell values from cell lists in same row
            Look at all columns and remove solved cell values from cell lists in the same column
            Look at all sectors and remove all solved cell values from cell lists in the same sector
        '''
        __resultDict = {}
        for nRow in range(0, 9):
            for nCol in range(0, 9):
                c = (nRow, nCol)
                res = list(range(1, 10))
                if self[nRow][nCol] == 0:
                    __resultDict[c] = res
                else:
                    __resultDict[c] = []
        # look at rows
        nRes = 1
        for r in range(0, 9):
            row = self[r]
            lres = []
            for c in range(0, 9):
                if (row[c] != 0):
                    lres.append(row[c])
                    #print('[{}] {} : ({},{}) -> {}'.format(nRes, row[c], r, c, __resultDict.get((r, c)))); nRes += 1;
            for result in lres:
                for c in range(0, 9):
                    ls = __resultDict.get((r, c))
                    if (result in ls):
                        #before = ls[:]
                        ls.remove(result)
                        #print('({}, {}) {} : {} remove {} ==> {}'.format(r, c, self[r][c], before, result, ls))
        # look at columns
        nRes = 1
        for c in range(0, 9):
            col = self.col(c)
            lres = []
            for r in range(0, 9):
                if (col[r] != 0):
                    lres.append(col[r])
                    #print('[{}] {} : ({},{}) -> {}'.format(nRes, col[r], r, c, __resultDict.get((r, c)))); nRes += 1;
            for result in lres:
                for r in range(0, 9):
                    ls = __resultDict.get((r, c))
                    if (result in ls):
                        #before = ls[:]
                        ls.remove(result)
                        #print('({}, {}) {} : {} remove {} ==> {}'.format(r, c, self[r][c], before, result, ls))
        # look at sectors
        nRes = 1
        for i in range(0, 3):
            for j in range(0, 3):
                sect = self.sector(i, j)
                lres = []
                for r in range(0, 3):
                    for c in range(0, 3):
                        x = i*3+r
                        y = j*3+c
                        if (sect[r][c] != 0):
                            lres.append(sect[r][c])
                            #print('[{}] sector({},{}) : {} : [{},{}] = ({},{}) -> {}'.format(nRes, i, j, sect[r][c], r, c, x, y, __resultDict.get((x, y)))); nRes += 1;
                for result in lres:
                    for r in range(0, 3):
                        for c in range(0, 3):
                            x = i*3+r
                            y = j*3+c
                            ls = __resultDict.get((x,y))
                            if (result in ls):
                                before = ls[:]
                                ls.remove(result)
                                #print('sector[{},{}]@({},{}) ({}, {}) {} : {} remove {} ==> {}'.format(i, j, r, c, x, y, self[x][y], before, result, ls))
        # look at rows, columns, sectors and see if any particular number has only one possible position
        # rows
        for ridx, row in enumerate(self.__data):
            # count the number of occurences in a line
            countdict = {key: [] for key in range(1, 10)}
            for cidx, c in enumerate(row):
                ls = __resultDict.get((ridx, cidx))
                for n in ls:
                    countdict[n].append((ridx, cidx))
            for n, coords in countdict.items():
                if (len(coords) == 1):
                    x, y = coords[0]
                    if (n not in self.col(y)) and (n not in self.get_sector_from_coord(x, y)):
                        #print('{} is unique to cell {} : {}'.format(n, (x, y), __resultDict.get((x, y))))
                        __resultDict[(x, y)] = [n]
        for cidx in range(0, 8):
            countdict = {key: [] for key in range(1, 10)}
            col = self.col(cidx)
            for ridx, n in enumerate(col):
                ls = __resultDict.get((ridx, cidx))
                for n in ls:
                    countdict[n].append((ridx, cidx))
            for n, coord in countdict.items():
                if (len(coords) == 1):
                    x, y = coords[0]
                    if (n not in self.row(x)) and (n not in self.get_sector_from_coord(x, y)):
                        #print('{} is unique to cell {} : {}'.format(n, (x, y), __resultDict.get((x, y))))
                        __resultDict[(x, y)] = [n]
        for i in range(0, 3):
            for j in range(0, 3):
                sect = self.sector(i, j)
                countdict = {key: [] for key in range(1, 10)}
                for r, row in enumerate(sect):
                    for c, col in enumerate(row):
                        x = i*3+r
                        y = j*3+c
                        ls = __resultDict.get((x, y))
                        for n in ls:
                            countdict[n].append((x, y))
                for n, coords in countdict.items():
                    if (len(coords) == 1):                        
                        x, y = coords[0]
                        if (n not in self.row(x)) and (n not in self.col(y)):
                            #print('{} is unique to cell {} : {}'.format(n, (x, y), __resultDict.get((x, y))))
                            __resultDict[(x, y)] = [n]

        return __resultDict

    def is_valid(self):
        ls = []
        for n in range(0, 9):
            row = self.row(n)
            for elmt in row:
                if elmt != 0:
                    if (row.count(elmt) > 1):
                        return False
            col = self.col(n)
            for elmt in col:
                if elmt != 0:
                    if (col.count(elmt) > 1):
                        return False
        for x in range(0, 3):
            for y in range(0, 3):
                sect = self.sector(x, y)
                for elmt in sect:
                    if (elmt != 0):
                        if (sum(r.count(elmt) for r in sect) > 1):
                            return False
        return True
     
    def assign(self, other):
        self.__data = []
        for ridx, row in enumerate(other.__data):
            self.__data.append([])
            for cidx, itm in enumerate(row):
                self.__data[ridx].append(itm)


def GuessAndCheck(puzzle:SudokuPuzzle, res:dict={}):
    
    if (puzzle.solved()):
        return True
    elif (not puzzle.is_valid()):
        return False

    if (not res):
        res = puzzle.get_possibilities()

    # if there are no possibilities for an unsolved cell, we have failed
    for coord, ls in res.items():
        if (puzzle[coord[0]][coord[1]] == 0) and len(ls) == 0:
            return False    

    #solved = {coord: ls[0] for coord, ls in res.items() if len(ls) == 1}
    #while (len(solved) > 0):
    #    for coord, n in solved.items():
    #        puzzle[coord[0]][coord[1]] = n
    #        res[coord].remove(n)
    #    # invalid "solutions" may exist in the results list: this can happen because after trying to reduce the puzzle, there is no way to avoid a conflict
    #    if (not puzzle.is_valid()):
    #        return False
    #    elif (puzzle.solved()):
    #        return True
    #    #res = puzzle.get_possibilities()
    #    solved = {coord: ls[0] for coord, ls in res.items() if len(ls) == 1}

    print('')
    puzzle.print()

    sorted_res = []
    for k in sorted(res, key=lambda k: len(res.get(k))):
        sorted_res.append((k, res.get(k)))

    tmp = SudokuPuzzle()
    tmp.assign(puzzle)
    
    # Barbara's method:
    # find a sector with the most solved cells. for every row and column common to that sector, look for binary choices:
    #       0 1 2   3 4 5   6 7 8
    #     +-------+-------+-------
    # [6] | . . . | 6 . 3 | . 7 .
    # [7] | 5 . 3 | 2 . 1 | . . .
    # [8] | 1 . 4 | . . . | . . . 
    #
    # for cells (6,4) and (7,4) we can deduce that because the left-most sector has a '4' in (8,2), there can not be
    # any 4's in (8,3), (8,4), or (8,5). After we do a depth first search after making an assumption (i.e., (7,4) we assume is 4),
    # and we reach a fail-state (without making further assumptions), because (7,4) cannot be 4, (6,4) MUST be 4.
    # If we do reach a fail-state without making further assumptions, we can safely eliminate the last assumption

    for cls in sorted_res:
        if (not cls[1]):
            continue
        coord = cls[0]
        ls    = cls[1]
        ##### Make Assumption: #####
        for poss in ls:
            tmp[coord[0]][coord[1]] = poss
            if (not GuessAndCheck(tmp)):
                tmp.assign(puzzle) # undo changes
                ls.remove(poss)
                # look at rows:
                countdict = {key: [] for key in range(1, 10)}
                for i, rcell in enumerate(tmp.row(coord[0])):
                    _coord = (coord[0], i)
                    l = res.get(_coord)
                    for n in l:
                        if (_coord != (coord)) or n != poss:
                            countdict[n].append(_coord)
                for n, d in countdict.items():
                    if len(d) is 1:
                        tmp[d[0][0]][d[0][1]] = n
                # look at columns
                countdict = {key: [] for key in range(1, 10)}
                for i, ccell in enumerate(tmp.col(coord[1])):
                    _coord = (i, coord[1])
                    l = res.get(_coord)
                    for n in l:
                        if (_coord != (coord)) or n != poss:
                            countdict[n].append(_coord)
                for n, d in countdict.items():
                    if len(d) is 1:
                        tmp[d[0][0]][d[0][1]] = n
                # look at sectors
                countdict = {key: [] for key in range(1, 10)}
                rsector, csector = (int(coord[0]/3), int(coord[1]/3))
                sector = tmp.sector(rsector, csector)
                for r, scell in enumerate(sector):
                    for c, cell in enumerate(scell):
                        _coord = (rsector*3+r, csector*3+c)
                        l = res.get(_coord)
                        for n in l:
                            if (_coord != (coord)) or n != poss:
                                countdict[n].append(_coord)
                for n, d in countdict.items():
                    if len(d) is 1:
                        tmp[d[0][0]][d[0][1]] = n
                # save deductions
                puzzle.assign(tmp)
            else:
                puzzle.assign(tmp) # save changes
                return True    
    return False


def main():
    
    start_time = time.time()

    for arg in sys.argv[1:]:
        print (arg)

    fpuzzle = open(sys.argv[1])
    puzzle = None
    strpuzzle = ''
    for line in fpuzzle:
        tmpline = line.translate({ord(c): None for c in '|+- \n'})
        strpuzzle += tmpline

    print(strpuzzle)
    puzzle = SudokuPuzzle(strpuzzle)
        
    if (puzzle == None):
        raise Exception('failed to initialize puzzle from file')
    
    print('')
    puzzle.print()
    GuessAndCheck(puzzle)    
    elapsed_time = time.time() - start_time
    print('\n---------------- solution ----------------\n')
    puzzle.print()
    print('\nelapsed time: {0:.2f} seconds'.format(elapsed_time))

if (__name__ == "__main__"):
    main()
