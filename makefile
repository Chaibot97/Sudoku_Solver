all : Sudoku Test

Sudoku:
	echo "#!/bin/bash" > Sudoku
	echo "python3 sudoku_solver.py \"\$$@\"" >> Sudoku
	chmod u+x Sudoku

Test:
	echo "#!/bin/bash" > Test
	echo "tar -zxf benchmarks.tar.gz" >> Test
	echo "python3 test.py \"\$$@\"" >> Test
	chmod u+x Test
