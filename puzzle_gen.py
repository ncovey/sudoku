import sudoku
import random
import multiprocessing

CHANCE_SET_VALUE = float(17.0/81.0)

MIN_FILLED_CELLS = 17
MIN_DIFFERENT_VALUES = 8

bSolutionFound = False

def isValid(puzzle:sudoku.SudokuPuzzle):
    if (not puzzle.is_valid()):
        return False
    num_filled_cells = 0
    countdict = {key: 0 for key in range(1, 10)}
    for nRow, row in enumerate(puzzle):
        for nCol, n in enumerate(row):
            if (n != 0):
                num_filled_cells += 1
                countdict[n] = 1
    num_diff_value = sum(countdict.values())
    if (num_filled_cells < MIN_FILLED_CELLS) or (num_diff_value < MIN_DIFFERENT_VALUES):
        return False
    else:
        print('')
        puzzle.print()
        print('num_filled_cells={} num_diff_value={}\n'.format(num_filled_cells, num_diff_value))
        return True


def generate_random(randpuzzle:sudoku.SudokuPuzzle):
    while(not isValid(randpuzzle)):
        randpuzzle.reset()
        for r, row in enumerate(randpuzzle):
            bValid = True
            for c, n in enumerate(row):
                fchance = random.uniform(0.0, 1.0)
                if (fchance <= CHANCE_SET_VALUE):
                    possible_values = [x for x in range(1, 10)]
                    randidx = random.randint(0, len(possible_values)-1)
                    val = possible_values[randidx]
                    while ((val in randpuzzle.row(r)) or (val in randpuzzle.col(c)) or (val in randpuzzle.get_sector_from_coord(r, c))):
                        possible_values.remove(val)
                        if len(possible_values) == 0:
                            bValid = False
                            break
                        randidx = random.randint(0, len(possible_values)-1)
                        val = possible_values[randidx]
                    if (not bValid): 
                        break
                    randpuzzle[r][c] = val
            if (not bValid): 
                break

def find_solution(puzzle:sudoku.SudokuPuzzle, q:multiprocessing.Queue):
    bSolved = sudoku.GuessAndCheck(puzzle)
    q.put(bSolved)
    q.put(puzzle)

def main():

    randpuzzle = sudoku.SudokuPuzzle('.................................................................................')
    
    generate_random(randpuzzle)
    tmp = sudoku.SudokuPuzzle()
    tmp.assign(randpuzzle)
    
    q = multiprocessing.Queue()

    while (True):
        p = multiprocessing.Process(target=find_solution, args=(randpuzzle,q))
        p.start()
        p.join(5)

        if p.is_alive():
            p.terminate()
            p.join()
        else:
            bFound = q.get()
            tmp = q.get()
            if (bFound == True):
                q.close()
                q.join_thread()
                break

        print("could not find a solution to puzzle... restarting\n")
        randpuzzle.reset()
        generate_random(randpuzzle)
        tmp.assign(randpuzzle)
        
    randpuzzle.print()
    print('\n---------------- solution ----------------\n')
    tmp.print()
    print('\nline form:')
    randpuzzle.printline()

    return

if (__name__ == "__main__"):
    main()
