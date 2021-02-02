"""
Sudoku solver
author: Lizhou Cai

run:
python3 sudoku_solver.py IN_FILE LEVEL(0-4)
"""

import numpy as np
import argparse
import sys
import time


def parseArg():
    """
    CMD argument parsing
    :return: the parser
    """
    parser = argparse.ArgumentParser(description='SAT solver')
    parser.add_argument('infile', nargs=1, type=argparse.FileType('r'))
    parser.add_argument('level', nargs='?', default=0, type=int)
    return parser


"""
Sudoku game
level represents the group of methods that is used
level:
0: bt, bt+cp1, bt+cp2, bt+cp3, bt+cp3+mrv
1: bt+cp1
2: bt+cp2
3: bt+cp3
4: bt+cp3+mrv
where:
bt: backtracking
cp1: one-candidate
cp2: cp1+naked-pair+hidden-pair
cp3: cp1+cp2+x-wing
mrv: Minimum Remaining Values
"""
class Sudoku:
    def __init__(self, grid, level):
        self.grid = grid
        self.n = self.grid.shape[0]
        self.steps = 0
        self.candidate = np.zeros((self.n, self.n, self.n), dtype=int)
        self.level = level
        self.time = time.time()
        sys.setrecursionlimit(2500)

    def __str__(self):
        res = ''
        for i in range(self.n):
            for j in range(self.n):
                n = self.grid[i][j]
                res += str(n) if n != 0 else '_'
                res += ' '
            res += '\n'
        return res

    def sub_block(self, r, c):
        """
        find the block (r,c) resides in
        """
        sub_n = self.n ** 0.5
        i, j = r // sub_n, c // sub_n
        rs, re = int(sub_n * i), int(sub_n * (i + 1))
        cs, ce = int(sub_n * j), int(sub_n * (j + 1))
        return rs, re, cs, ce

    def check_valid(self):
        """
        check if the whole puzzle is finished and valid
        """
        if 0 in self.grid:
            return False
        for r in range(self.n):
            for c in range(self.n):
                n = self.grid[r, c]
                self.grid[r, c] = 0
                if not self.move_valid(n, r, c):
                    return False
                self.grid[r, c] = n
        return True

    def move_valid(self, n, r, c):
        """
        check if n is a valid digit to fill in at (r,c)
        """
        rs, re, cs, ce = self.sub_block(r, c)
        return n not in self.grid[r, :] and n not in self.grid[:, c] and \
               n not in self.grid[rs:re, cs:ce]

    """
    Sudoku solver 
    """
    def solve(self):

        for r in range(self.n):
            for c in range(self.n):
                if self.grid[r][c] != 0:
                    continue
                for n in range(1, self.n + 1):
                    self.candidate[r][c][n - 1] = 1 if self.move_valid(n, r, c) else 0

        if self.back_track():
            t = time.time() - self.time
            assert self.check_valid()
            return str(self), self.steps, t
        else:
            t = time.time() - self.time
            return None, self.steps, t

    def back_track(self):
        """
        Solver with back_tracking, Constrain propagation and minimum remaining values
        """
        if 0 not in self.grid:
            return True

        self.steps += 1

        ind = np.where(self.grid == 0)
        t = 0
        if self.level >= 4:
            t = np.argmin(np.sum(self.candidate[ind], axis=-1))
        r, c = ind[0][t], ind[1][t]
        moves = np.where(self.candidate[r, c] == 1)[0]
        for n in moves:
            grid_backup = np.where(self.grid == 0)
            cand_backup = np.where(self.candidate == 1)
            self.grid[r, c] = n + 1
            self.eliminate(n, r, c)
            self.constrain_prop()
            res = self.back_track()
            if res:
                return True
            else:
                self.grid[grid_backup] = 0
                self.candidate[cand_backup] = 1
        return False

    def eliminate(self, n, r, c):
        """
        eliminate candidates after fill in a value
        """
        rs, re, cs, ce = self.sub_block(r, c)
        t = self.candidate[r, c, n]
        self.candidate[r, :, n] = 0
        self.candidate[:, c, n] = 0
        self.candidate[rs:re, cs:ce, n] = 0
        self.candidate[r, c, n] = t

    def constrain_prop(self):
        """
        propagate constrains (eliminate candidates)
        """
        if self.level >= 3:
            self.x_wing()
        if self.level >= 2:
            self.naked_pair()
            self.hidden_pairs()
        if self.level >= 1:
            self.single_candidate()

    """
    cp3 strategies
    """
    def x_wing(self):
        rows, cols = np.where(np.sum(self.candidate, axis=2) >= 2)
        pairs = []
        values, counts = np.unique(rows, return_counts=True)
        for r in values[counts > 1]:
            cs = cols[rows == r]
            for i in range(len(cs)):
                for j in range(i + 1, len(cs)):
                    s = self.candidate[r, cs[i]] + self.candidate[r, cs[j]]
                    if len(s[s == 2]) >= 1:
                        for n in np.where(s == 2)[0]:
                            if np.sum(self.candidate[r, :, n]) == 2:
                                pairs.append(((r, cs[i]), (r, cs[j]), n))
        values, counts = np.unique(cols, return_counts=True)
        for c in values[counts > 1]:
            rs = rows[cols == c]
            for i in range(len(rs)):
                for j in range(i + 1, len(rs)):
                    s = self.candidate[rs[i],c] + self.candidate[rs[j],c]
                    if len(s[s == 2]) >= 1:
                        for n in np.where(s == 2)[0]:
                            if np.sum(self.candidate[:, c, n]) == 2:
                                pairs.append(((rs[i],c), (rs[j],c), n))
        for i in range(len(pairs)):
            for j in range(i+1,len(pairs)):
                p1, p2 = pairs[i], pairs[j]
                if p1[-1] != p2[-1]:
                    continue
                (r11, c11), (r12, c12), n1 = p1
                (r21, c21), (r22, c22), n2 = p2
                if self.candidate[r11, c11][n1] != 1 or self.candidate[r12, c12][n1] != 1 \
                        or self.candidate[r21, c21][n2] != 1 or self.candidate[r22, c22][n2] != 1:
                    continue
                # x-wing in rows
                if r11 == r12 and r21 == r22 and c11 == c21 and c12 == c22:
                    self.candidate[:, c11, n1] = 0
                    self.candidate[:, c12, n1] = 0
                # x-wing in cols
                if c11 == c12 and c21 == c22 and r11 == r21 and r12 == r22:
                    self.candidate[r11, :, n1] = 0
                    self.candidate[r12, :, n1] = 0
                self.candidate[r11, c11, n1] = 1
                self.candidate[r12, c12, n1] = 1
                self.candidate[r21, c21, n1] = 1
                self.candidate[r22, c22, n1] = 1

    """
    cp2 strategies
    """
    def naked_pair(self):
        rows, cols = np.where(np.sum(self.candidate, axis=2) == 2)
        pairs = []
        values, counts = np.unique(rows, return_counts=True)
        for r in values[counts > 1]:
            cs = cols[rows == r]
            for i in range(len(cs)):
                for j in range(i + 1, len(cs)):
                    if np.all(self.candidate[r, cs[i]] == self.candidate[r, cs[j]]):
                        pairs.append(((r, cs[i]), (r, cs[j])))
        values, counts = np.unique(cols, return_counts=True)
        for c in values[counts > 1]:
            rs = rows[cols == c]
            for i in range(len(rs)):
                for j in range(i + 1, len(rs)):
                    if np.all(self.candidate[rs[i], c] == self.candidate[rs[j], c]):
                        pairs.append(((rs[i], c), (rs[j], c)))
        for pair in pairs:
            (r1, c1), (r2, c2) = pair
            if not np.all(self.candidate[r1, c1] == self.candidate[r2, c2]):
                continue
            n = np.where(self.candidate[r1, c1] == 1)[0]
            if r1 == r2:
                self.candidate[r1, :, n] = 0
            else:
                assert c1 == c2
                self.candidate[:, c1, n] = 0
            self.candidate[r1, c1, n] = 1
            self.candidate[r2, c2, n] = 1

    def hidden_pairs(self):
        rows, cols = np.where(np.sum(self.candidate, axis=2) >= 2)
        values, counts = np.unique(rows, return_counts=True)
        for r in values[counts > 1]:
            cs = cols[rows == r]
            for i in range(len(cs)):
                for j in range(i + 1, len(cs)):
                    s = self.candidate[r, cs[i]] + self.candidate[r, cs[j]]
                    if len(s[s == 2]) == 2 and np.sum(self.candidate[r, :, np.where(s == 2)[0]]) == 4:
                        self.candidate[r, cs[i]] = np.where(s == 2, 1, 0)
                        self.candidate[r, cs[j]] = np.where(s == 2, 1, 0)
        values, counts = np.unique(cols, return_counts=True)
        for c in values[counts > 1]:
            rs = rows[cols == c]
            for i in range(len(rs)):
                for j in range(i + 1, len(rs)):
                    s = self.candidate[rs[i], c] + self.candidate[rs[j], c]
                    if len(s[s == 2]) == 2 and np.sum(self.candidate[:, c, np.where(s == 2)[0]]) == 4:
                        self.candidate[rs[i], c] = np.where(s == 2, 1, 0)
                        self.candidate[rs[j], c] = np.where(s == 2, 1, 0)

    """
    cp1 strategies
    """
    def single_candidate(self):
        ind = np.where(np.sum(self.candidate, axis=2) == 1)
        if len(ind[0]) > 0:
            r, c = ind[0][0], ind[1][0]
            n = np.where(self.candidate[r, c] == 1)[0][0]
            self.grid[r, c] = n + 1
            self.candidate[r, c, n] = 0
            self.eliminate(n, r, c)
            self.single_candidate()


def parse_input(f):
    """
    Read in the input file and generate a numpy grid
    """
    grid = np.zeros((9, 9), dtype=int)
    for i, line in enumerate(f):
        line = list(line.strip())
        for j, n in enumerate(line):
            grid[i][j] = n if n != '_' else 0
    return grid


def run():
    args = parseArg().parse_args()
    grid = parse_input(args.infile[0])
    game = Sudoku(grid, args.level)
    solution, steps, runtime = game.solve()
    print('time(s):', runtime)
    print('Steps:', steps)
    print(solution)


if __name__ == '__main__':
    run()
