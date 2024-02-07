# Joe Shymanski
# Sudoku Solver
import time
import copy

class Cell:
    def __init__(self, val):
        self.value = int(val) if str(val) in "123456789" else 0
        self.candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9] if self.value == 0 else [self.value]

    def hasSingleCandidate(self):
        return len(self.candidates) == 1


class Table:
    def __init__(self, initcells):
        self.cells = initcells

    def __str__(self):
        ret = ""
        for cell in self.cells:
            val = str(cell.value) if cell.value != 0 else " "
            ret += val + " "
            if (self.cells.index(cell) + 1) % 9 == 0:
                ret = ret[:-1] + "\n"
        if ret.endswith("\n"):
            ret = ret[:-1]
        return ret

    def rowCells(self, row):
        return self.cells[row * 9:row * 9 + 9]

    def colCells(self, col):
        return self.cells[col::9]

    def boxCells(self, box):
        return self.cells[(box // 3) * 27 + (box % 3) * 3:(box // 3) * 27 + (box % 3) * 3 + 3] + \
               self.cells[(box // 3) * 27 + (box % 3) * 3 + 9:(box // 3) * 27 + (box % 3) * 3 + 12] + \
               self.cells[(box // 3) * 27 + (box % 3) * 3 + 18:(box // 3) * 27 + (box % 3) * 3 + 21]

    def cellsLeft(self):
        return [x for x in self.cells if x.value == 0]

    def numCandidatesLeft(self):
        candidatesLeft = [x.candidates for x in self.cellsLeft()]
        numCandidatesLeft = 0
        for candidates in candidatesLeft:
            numCandidatesLeft += len(candidates)
        return numCandidatesLeft

    def checkSameBox(self, icell, jcell):
        i = self.cells.index(icell)
        j = self.cells.index(jcell)
        irow = i // 9
        jrow = j // 9
        icol = i % 9
        jcol = j % 9
        return (irow // 3 == jrow // 3) and (icol // 3 == jcol // 3)

    def cellCausesError(self, cell, filledCells=None):
        if filledCells is None:
            filledCells = [x for x in self.cells if x.value != 0]
        error = False
        c = self.cells.index(cell)
        crow = c // 9
        ccol = c % 9
        for fcell in filledCells:
            f = self.cells.index(fcell)
            frow = f // 9
            fcol = f % 9
            if (crow == frow or ccol == fcol or self.checkSameBox(cell, fcell)) and cell.value == fcell.value:
                error = True
                break
        return error

    def removeImpossibleCandidates(self, cell, printReceipt=True):
        receipt = ""
        c = self.cells.index(cell)
        crow = c // 9
        ccol = c % 9
        filledCells = [x for x in self.cells if x.value != 0]
        for fcell in filledCells:
            f = self.cells.index(fcell)
            frow = f // 9
            fcol = f % 9
            if (crow == frow or
                ccol == fcol or
                self.checkSameBox(cell, fcell)) and \
                    fcell.value in cell.candidates:
                cell.candidates.remove(fcell.value)
        receipt += "Row " + str(crow + 1) + " Column " + str(ccol + 1) + " " + str(cell.candidates) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findNakedSingles(self, printReceipt=True):
        receipt = ""
        for cell in self.cellsLeft():
            c = self.cells.index(cell)
            row = c // 9
            col = c % 9
            if cell.hasSingleCandidate():
                cell.value = cell.candidates[0]
                receipt += "Row " + str(row + 1) + " Column " + str(col + 1) + " " + str(cell.candidates) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findHiddenSingles(self, printReceipt=True):
        receipt = ""
        for type in range(3):
            removed = False
            for group in range(9):
                groupName = ""
                groupCells = []
                if type == 0:
                    groupName = "Row"
                    groupCells = self.rowCells(group)
                if type == 1:
                    groupName = "Column"
                    groupCells = self.colCells(group)
                if type == 2:
                    groupName = "Box"
                    groupCells = self.boxCells(group)
                emptyCellCandidatesInGroup = [x.candidates for x in groupCells if x.value == 0]
                counts = {}
                for candidates in emptyCellCandidatesInGroup:
                    for num in candidates:
                        if num not in counts:
                            counts[num] = 0
                        counts[num] += 1
                singles = [x for x in counts if counts[x] == 1]
                if singles:
                    emptyCells = [x for x in groupCells if x.value == 0]
                    for single in singles:
                        for cell in emptyCells:
                            if single in cell.candidates:
                                cell.candidates = [single]
                                cell.value = single
                    receipt += groupName + " " + str(group + 1) + " " + str(singles) + "\n"
                    removed = True
            if removed:
                break
        if printReceipt and receipt:
            print(receipt, end="")

    def findNakedPairs(self, printReceipt=True):
        receipt = ""
        for type in range(3):
            for group in range(9):
                groupName = ""
                groupCells = []
                if type == 0:
                    groupName = "Row"
                    groupCells = self.rowCells(group)
                if type == 1:
                    groupName = "Column"
                    groupCells = self.colCells(group)
                if type == 2:
                    groupName = "Box"
                    groupCells = self.boxCells(group)
                emptyCells = [x for x in groupCells if x.value == 0]
                pairs = []
                if len(emptyCells) >= 2:
                    for icell in emptyCells:
                        if len(icell.candidates) == 2:
                            ie = emptyCells.index(icell)
                            for jcell in emptyCells[ie + 1:]:
                                if icell.candidates == jcell.candidates:
                                    removed = False
                                    for cell in emptyCells:
                                        if cell is not icell and cell is not jcell:
                                            before = cell.candidates[:]
                                            cell.candidates = [x for x in cell.candidates if x not in icell.candidates]
                                            after = cell.candidates[:]
                                            if before != after:
                                                removed = True
                                    if removed:
                                        pairs.append(icell.candidates)
                if pairs:
                    receipt += groupName + " " + str(group + 1) + " " + str(pairs) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findHiddenPairs(self, printReceipt=True):
        receipt = ""
        for type in range(3):
            for group in range(9):
                groupName = ""
                groupCells = []
                if type == 0:
                    groupName = "Row"
                    groupCells = self.rowCells(group)
                if type == 1:
                    groupName = "Column"
                    groupCells = self.colCells(group)
                if type == 2:
                    groupName = "Box"
                    groupCells = self.boxCells(group)
                emptyCellCandidatesInGroup = [x.candidates for x in groupCells if x.value == 0]
                counts = {}
                for candidates in emptyCellCandidatesInGroup:
                    for num in candidates:
                        if num not in counts:
                            counts[num] = 0
                        counts[num] += 1
                doubles = [x for x in counts if counts[x] == 2]
                if doubles:
                    emptyCells = [x for x in groupCells if x.value == 0]
                    for double1 in doubles[:]:
                        di = doubles.index(double1)
                        pair = []
                        for cell in emptyCells:
                            if double1 in cell.candidates:
                                pair.append(cell)
                        if len(pair) == 2 and len(pair[0].candidates + pair[1].candidates) > 4:
                            for double2 in doubles[di + 1:]:
                                if double2 in pair[0].candidates and double2 in pair[1].candidates:
                                    nakedPair = [double1, double2]
                                    pair[0].candidates = nakedPair[:]
                                    pair[1].candidates = nakedPair[:]
                                    receipt += groupName + " " + str(group + 1) + " " + str(nakedPair) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findPointingPairs(self, printReceipt=True):
        self.findPointingPairsByRow(printReceipt)
        self.findPointingPairsByCol(printReceipt)

    def findPointingPairsByRow(self, printReceipt=True):
        receipt = ""
        for row in range(9):
            rowCells = self.rowCells(row)
            emptyCellCandidatesInRow = [x.candidates for x in rowCells if x.value == 0]
            counts = {}
            for candidates in emptyCellCandidatesInRow:
                for num in candidates:
                    if num not in counts:
                        counts[num] = 0
                    counts[num] += 1
            pairNums = [x for x in counts if counts[x] == 2]
            emptyCellsInRow = [x for x in rowCells if x.value == 0]
            for pairNum in pairNums[:]:
                pair = []
                for emptyCellInRow in emptyCellsInRow:
                    if pairNum in emptyCellInRow.candidates:
                        pair.append(emptyCellInRow)
                i = self.cells.index(pair[0])
                icol = i % 9
                if self.checkSameBox(pair[0], pair[1]):
                    box = row // 3 * 3 + icol // 3
                    boxCells = self.boxCells(box)
                    emptyCellsInBox = [x for x in boxCells if x.value == 0]
                    removed = False
                    for emptyCellInBox in emptyCellsInBox:
                        if emptyCellInBox not in pair and pairNum in emptyCellInBox.candidates:
                            emptyCellInBox.candidates.remove(pairNum)
                            removed = True
                    if not removed:
                        pairNums.remove(pairNum)
                else:
                    pairNums.remove(pairNum)
            if pairNums:
                receipt += "Row " + str(row + 1) + " " + str(pairNums) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findPointingPairsByCol(self, printReceipt=True):
        receipt = ""
        for col in range(9):
            colCells = self.colCells(col)
            emptyCellCandidatesInCol = [x.candidates for x in colCells if x.value == 0]
            counts = {}
            for candidates in emptyCellCandidatesInCol:
                for num in candidates:
                    if num not in counts:
                        counts[num] = 0
                    counts[num] += 1
            pairNums = [x for x in counts if counts[x] == 2]
            emptyCellsInCol = [x for x in colCells if x.value == 0]
            for pairNum in pairNums[:]:
                pair = []
                for emptyCellInCol in emptyCellsInCol:
                    if pairNum in emptyCellInCol.candidates:
                        pair.append(emptyCellInCol)
                i = self.cells.index(pair[0])
                irow = i // 9
                if self.checkSameBox(pair[0], pair[1]):
                    box = irow // 3 * 3 + col // 3
                    boxCells = self.boxCells(box)
                    emptyCellsInBox = [x for x in boxCells if x.value == 0]
                    removed = False
                    for emptyCellInBox in emptyCellsInBox:
                        if emptyCellInBox not in pair and pairNum in emptyCellInBox.candidates:
                            emptyCellInBox.candidates.remove(pairNum)
                            removed = True
                    if not removed:
                        pairNums.remove(pairNum)
                else:
                    pairNums.remove(pairNum)
            if pairNums:
                receipt += "Column " + str(col + 1) + " " + str(pairNums) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findNakedTriples(self, printReceipt=True):
        receipt = ""
        for type in range(3):
            for group in range(9):
                groupName = ""
                groupCells = []
                if type == 0:
                    groupName = "Row"
                    groupCells = self.rowCells(group)
                if type == 1:
                    groupName = "Column"
                    groupCells = self.colCells(group)
                if type == 2:
                    groupName = "Box"
                    groupCells = self.boxCells(group)
                emptyCells = [x for x in groupCells if x.value == 0]
                trips = []
                if len(emptyCells) >= 3:
                    for icell in emptyCells:
                        if len(icell.candidates) <= 3:
                            ie = emptyCells.index(icell)
                            for jcell in emptyCells[ie + 1:]:
                                if len(jcell.candidates) <= 3:
                                    je = emptyCells.index(jcell)
                                    for kcell in emptyCells[je + 1:]:
                                        if len(kcell.candidates) <= 3:
                                            iandj = list(set(icell.candidates + jcell.candidates))
                                            iandk = list(set(icell.candidates + kcell.candidates))
                                            jandk = list(set(jcell.candidates + kcell.candidates))
                                            ijk = list(set(iandj + iandk + jandk))
                                            if len(ijk) == 3:
                                                removed = False
                                                for cell in emptyCells:
                                                    if cell is not icell and cell is not jcell and cell is not kcell:
                                                        before = cell.candidates[:]
                                                        cell.candidates = [x for x in cell.candidates if x not in ijk]
                                                        after = cell.candidates[:]
                                                        if before != after:
                                                            removed = True
                                                if removed:
                                                    trips.append(ijk)
                if trips:
                    receipt += groupName + " " + str(group + 1) + " " + str(trips) + "\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findXWings(self, printReceipt=True):
        self.findXWingsByRow(printReceipt)
        self.findXWingsByCol(printReceipt)

    def findXWingsByRow(self, printReceipt=True):
        receipt = ""
        xWingNums = {}
        for row in range(9):
            rowCells = self.rowCells(row)
            emptyCellCandidatesInRow = [x.candidates for x in rowCells if x.value == 0]
            rowCounts = {}
            for candidates in emptyCellCandidatesInRow:
                for num in candidates:
                    if num not in rowCounts:
                        rowCounts[num] = 0
                    rowCounts[num] += 1
            pairNums = [x for x in rowCounts if rowCounts[x] == 2]
            emptyCellsInRow = [x for x in rowCells if x.value == 0]
            for pairNum in pairNums[:]:
                pair = []
                for emptyCellInRow in emptyCellsInRow:
                    if pairNum in emptyCellInRow.candidates:
                        pair.append(emptyCellInRow)
                if pairNum not in xWingNums:
                    xWingNums[pairNum] = []
                xWingNums[pairNum].append(pair)
        for xWingNum in dict(xWingNums):
            if len(xWingNums[xWingNum]) < 2:
                del xWingNums[xWingNum]
            else:
                for pair1 in xWingNums[xWingNum]:
                    pair1i = xWingNums[xWingNum].index(pair1)
                    row1 = self.cells.index(pair1[0]) // 9
                    icol1 = self.cells.index(pair1[0]) % 9
                    jcol1 = self.cells.index(pair1[1]) % 9
                    for pair2 in xWingNums[xWingNum][pair1i + 1:]:
                        row2 = self.cells.index(pair2[0]) // 9
                        icol2 = self.cells.index(pair2[0]) % 9
                        jcol2 = self.cells.index(pair2[1]) % 9
                        if icol1 == icol2 and jcol1 == jcol2:
                            removed = False
                            emptyCellsInICol = [x for x in self.colCells(icol1) if x.value == 0 and x not in pair1 and x not in pair2]
                            emptyCellsInJCol = [x for x in self.colCells(jcol1) if x.value == 0 and x not in pair1 and x not in pair2]
                            emptyCellsInIJCols = emptyCellsInICol + emptyCellsInJCol
                            for emptyCellInIJCols in emptyCellsInIJCols:
                                if xWingNum in emptyCellInIJCols.candidates:
                                    emptyCellInIJCols.candidates.remove(xWingNum)
                                    removed = True
                            if removed:
                                receipt += "Rows " + str(row1 + 1) + " and " + str(row2 + 1) + " [" + str(xWingNum) + "]\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def findXWingsByCol(self, printReceipt=True):
        receipt = ""
        xWingNums = {}
        for col in range(9):
            colCells = self.colCells(col)
            emptyCellCandidatesInCol = [x.candidates for x in colCells if x.value == 0]
            colCounts = {}
            for candidates in emptyCellCandidatesInCol:
                for num in candidates:
                    if num not in colCounts:
                        colCounts[num] = 0
                    colCounts[num] += 1
            pairNums = [x for x in colCounts if colCounts[x] == 2]
            emptyCellsInCol = [x for x in colCells if x.value == 0]
            for pairNum in pairNums[:]:
                pair = []
                for emptyCellInCol in emptyCellsInCol:
                    if pairNum in emptyCellInCol.candidates:
                        pair.append(emptyCellInCol)
                if pairNum not in xWingNums:
                    xWingNums[pairNum] = []
                xWingNums[pairNum].append(pair)
        for xWingNum in dict(xWingNums):
            if len(xWingNums[xWingNum]) < 2:
                del xWingNums[xWingNum]
            else:
                for pair1 in xWingNums[xWingNum]:
                    pair1i = xWingNums[xWingNum].index(pair1)
                    col1 = self.cells.index(pair1[0]) % 9
                    irow1 = self.cells.index(pair1[0]) // 9
                    jrow1 = self.cells.index(pair1[1]) // 9
                    for pair2 in xWingNums[xWingNum][pair1i + 1:]:
                        col2 = self.cells.index(pair2[0]) % 9
                        irow2 = self.cells.index(pair2[0]) // 9
                        jrow2 = self.cells.index(pair2[1]) // 9
                        if irow1 == irow2 and jrow1 == jrow2:
                            removed = False
                            emptyCellsInIRow = [x for x in self.rowCells(irow1) if x.value == 0 and x not in pair1 and x not in pair2]
                            emptyCellsInJRow = [x for x in self.rowCells(jrow1) if x.value == 0 and x not in pair1 and x not in pair2]
                            emptyCellsInIJRows = emptyCellsInIRow + emptyCellsInJRow
                            for emptyCellInIJRows in emptyCellsInIJRows:
                                if xWingNum in emptyCellInIJRows.candidates:
                                    emptyCellInIJRows.candidates.remove(xWingNum)
                                    removed = True
                            if removed:
                                receipt += "Columns " + str(col1 + 1) + " and " + str(col2 + 1) + " [" + str(xWingNum) + "]\n"
        if printReceipt and receipt:
            print(receipt, end="")

    def bruteForce(self, filledCells, cell, emptyCells, printReceipt=True):
        foundTrueValue = False
        while not foundTrueValue:
            while cell.value not in cell.candidates and cell.value < 9:
                cell.value += 1
            if not self.cellCausesError(cell, filledCells):
                if not emptyCells:
                    cell.candidates = [cell.value]
                    if printReceipt:
                        print(self)
                        print("Solved")
                    return True
                else:
                    filledTmp = filledCells[:]
                    emptyTmp = emptyCells[:]
                    filledTmp.append(cell)
                    cellTmp = emptyTmp.pop(0)
                    cellTmp.value = 1
                    foundTrueValue = self.bruteForce(filledTmp, cellTmp, emptyTmp, printReceipt)
                    if not foundTrueValue:
                        if cell.value == 9:
                            if printReceipt:
                                cell.value = "_"
                                print(self)
                                print("Stuck")
                            cell.value = 0
                            return False
                        else:
                            cell.value += 1
                    else:
                        cell.candidates = [cell.value]
                        return True
            else:
                if cell.value == 9:
                    if printReceipt:
                        cell.value = "_"
                        print(self)
                        print("Stuck")
                    cell.value = 0
                    return False
                else:
                    cell.value += 1

    def bruteForceSolve(self, printReceipt=True):
        emptyCells = []
        filledCells = []
        for cell in self.cells:
            self.removeImpossibleCandidates(cell, False)
            if cell.value == 0:
                emptyCells.append(cell)
            else:
                filledCells.append(cell)
        cell = emptyCells.pop(0)
        cell.value = 1
        self.bruteForce(filledCells, cell, emptyCells, printReceipt)

    def deductiveSolve(self, printReceipt=True, order=1):
        functions = {
            1: [self.findNakedSingles, "Finding Naked Singles"],
            2: [self.findHiddenSingles, "Finding Hidden Singles"],
            3: [self.findNakedPairs, "Finding Naked Pairs"],
            4: [self.findHiddenPairs, "Finding Hidden Pairs"],
            5: [self.findPointingPairs, "Finding Pointing Pairs"],
            6: [self.findNakedTriples, "Finding Naked Triples"],
            7: [self.findXWings, "Finding X-Wings"]
        }
        orders = {
            1: [1, 2, 3, 4, 5, 6, 7],
            2: [1, 2, 3, 4, 5, 7, 6],
            3: [1, 2, 3, 4, 6, 5, 7],
            4: [1, 2, 3, 4, 6, 7, 5],
            5: [1, 2, 3, 4, 7, 5, 6],
            6: [1, 2, 3, 4, 7, 6, 5],
            7: [1, 2, 3, 5, 4, 6, 7],
            8: [1, 2, 3, 5, 4, 7, 6],
            9: [1, 2, 3, 5, 6, 4, 7],
            10: [1, 2, 3, 5, 6, 7, 4],
            11: [1, 2, 3, 5, 7, 4, 6],
            12: [1, 2, 3, 5, 7, 6, 4],
            13: [1, 2, 3, 6, 4, 5, 7],
            14: [1, 2, 3, 6, 4, 7, 5],
            15: [1, 2, 3, 6, 5, 4, 7],
            16: [1, 2, 3, 6, 5, 7, 4],
            17: [1, 2, 3, 6, 7, 4, 5],
            18: [1, 2, 3, 6, 7, 5, 4]
        }
        solved = False
        stuck = False
        stepNum = 0
        if printReceipt:
            print(self)
        while not solved and not stuck:
            stepNum += 1
            if printReceipt:
                print("Step " + str(stepNum) + ":")
                print("Remaining Candidates")
            for cell in self.cellsLeft():
                self.removeImpossibleCandidates(cell, printReceipt)
            numCellsLeftBefore = len(self.cellsLeft())
            numCandidatesLeftBefore = self.numCandidatesLeft()
            for function in orders[order]:
                if printReceipt:
                    print(functions[function][1])
                functions[function][0](printReceipt)
                if self.numCandidatesLeft() != numCandidatesLeftBefore:
                    break
            if self.numCandidatesLeft() == numCandidatesLeftBefore:
                if printReceipt:
                    print("Solving with Brute Force")
                self.bruteForceSolve(False)
            numCellsLeftAfter = len(self.cellsLeft())
            numCandidatesLeftAfter = self.numCandidatesLeft()
            if printReceipt:
                print(self)
                print("Cells Filled", numCellsLeftBefore - numCellsLeftAfter)
                print("Candidates Removed", numCandidatesLeftBefore - numCandidatesLeftAfter)
            if not self.cellsLeft():
                solved = True
                print("Solved")
            elif numCandidatesLeftAfter == numCandidatesLeftBefore:
                stuck = True
                print("Stuck")


def testRuns():
    numRuns = 1
    for run in range(numRuns):
        print("Run", run + 1)
        file = open("SudokuTable.txt", "r")
        line = ""
        tableNum = 0
        totalTime = 0
        while not line:
            tableNum += 1
            print("Table", tableNum)
            cells = []
            for n in range(9):
                line = file.readline()
                for data in line.split():
                    cells.append(Cell(data))
            sudokuTable = Table(copy.deepcopy(cells))
            start = time.time()
            sudokuTable.deductiveSolve()
            end = time.time()
            duration = end - start
            totalTime += duration
            print(duration, "seconds")
            line = file.readline()[:-1]
        print("Total Time", totalTime, "seconds")


if __name__ == "__main__":
    testRuns()
