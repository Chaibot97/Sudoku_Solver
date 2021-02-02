# Sudoku Solver
### Prerequisites
* `numpy`

### make
       make
### Run 
       ./Sudoku INFILE LEVEL(0-4)
### Benchmarking
       ./Test
 
### Stratagies
- bt: backtracking
- cp1: one-candidate
- cp2: cp1+naked-pair+hidden-pair
- cp3: cp1+cp2+x-wing
- mrv: Minimum Remaining Values

### Method Level(0-4)
- L1:'bt'
- L2:'bt+cp1'
- L3:'bt+cp2'
- L4:'bt+cp3'
- L5:'bt+cp3+mrv'
