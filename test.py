"""
Sudoku solver benchmark
author: Lizhou Cai

run:
python3 test.py
"""

import os
from sudoku_solver import Sudoku, parse_input

benchmark_dir = './benchmarks'
levels = ['easy', 'medium', 'hard']
methods = [0, 1, 2, 3, 4]
methods_name = ['bt', 'bt+cp1', 'bt+cp2', 'bt+cp3', 'bt+cp3+mrv']
stats = []
comment = '''
It turns out that the beginner level strategy (1-candidate) and branching heuristic (min remaining vals) 
are the most efficient, since they make the most improvement in performance (step and time).
Higher level strategies does reduce the # of steps, but the overhead of checking the patterns every step is too high
and the frequency of occurrence of these patterns is too low.
(step-time tradeoff is too high)
It turns out that these complex strategies are best designed for human, 
probably because human are more efficient at pattern discovering than brute force counting.
'''


def run():
    for method in methods:
        stats.append([])
        for j, level in enumerate(levels):
            stats[method].append([])
            sub_dir = benchmark_dir + '/' + level
            puzzle_list = os.listdir(sub_dir)
            puzzle_list = sorted([name for name in puzzle_list
                           if 'in' in name.lower()])
            for puzzle in puzzle_list:
                puzzle_dir = sub_dir + '/' + puzzle
                with open(puzzle_dir) as f:
                    grid = parse_input(f)
                    game = Sudoku(grid, method)
                    solution, steps, runtime = game.solve()
                    stats[method][j].append((puzzle, steps, runtime))
                    assert solution != None
                    print(puzzle, methods_name[method],'Steps:', steps, 'time(s):',runtime)

    print()
    print('bt: backtracking')
    print('cp1: one-candidate')
    print('cp2: cp1+naked-pair+hidden-pair')
    print('cp3: cp1+cp2+x-wing')
    print('mrv: Minimum Remaining Values')
    print()
    print('Average backtracking steps and runtime:')
    print('tuples are in the format of (steps, time in milliseconds)')
    print('puzzle_level, bt, bt+cp1, bt+cp2, bt+cp3, bt+cp3+mrv')
    for j, level in enumerate(levels):
        stat = []
        for method in methods:
            time = 0
            step = 0
            count = len(stats[method][j])
            for p in stats[method][j]:
                time += p[2]
                step += p[1]
            stat.append('({}, {:.2f})'.format(step // count, time * 1000 / count))
        print(level + ',' + ','.join(stat))

    print(comment)


if __name__ == '__main__':
    run()
