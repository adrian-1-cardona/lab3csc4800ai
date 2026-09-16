# csc 4800 ai lab 3

adrian cardona

## lab overview

this lab is about uninformed search algorithms and how they behave on a navigation problem. i made a random weighted grid where the top left cell is the start and the bottom right cell is the goal. blocked cells act like buildings or closed roads, and the other cells have travel costs from 1 through 9.

this project implements:

- breadth-first search (bfs)
- depth-first search (dfs)
- uniform-cost search (ucs)
- iterative deepening depth-first search (iddfs)

all four algorithms run on the same map, so their results can be compared fairly.

## how to run it

this project uses python 3.10 or newer and does not need any outside packages.

run the main file:

```bash
python3 main.py
```

run one algorithm:

```bash
python3 main.py --algorithm bfs
python3 main.py --algorithm dfs
python3 main.py --algorithm ucs
python3 main.py --algorithm iddfs
```

change the map settings:

```bash
python3 main.py --rows 10 --cols 10 --obstacles 0.25 --seed 20
```

show the comparison table without printing every path:

```bash
python3 main.py --hide-paths
```

make a map that is allowed to have no solution:

```bash
python3 main.py --obstacles 0.5 --allow-unsolvable
```

see all options:

```bash
python3 main.py --help
```

## map symbols

- `S` is the starting cell
- `G` is the goal cell
- `#` is a blocked cell
- `*` is part of the path found by an algorithm
- a number is the cost of entering that cell

movement is allowed up, right, down, and left. diagonal movement is not allowed. the start and goal are always open. by default, the generator protects one random route so the map has a solution. the `--allow-unsolvable` option turns that protection off.

## how each search works

### breadth-first search

bfs uses a queue and checks the grid one level at a time. it finds a path with the fewest moves because every move increases the depth by one. it does not consider the cell weights when choosing a path, so the shallowest path may cost more.

### depth-first search

dfs uses a stack and follows one branch as far as possible before trying another branch. it can find a solution with less frontier space in some cases, but the first solution is not guaranteed to have the fewest moves or the lowest cost. visited cells prevent it from getting stuck in cycles.

### uniform-cost search

ucs uses a priority queue and always expands the path with the lowest total cost so far. if it finds a cheaper route to a cell, it replaces the older route. because all grid costs are positive, ucs is guaranteed to return a path with the lowest total travel cost.

### iterative deepening search

iddfs repeats depth-first search with limits of 0, 1, 2, and so on. it gets the shallow-path guarantee of bfs while using a depth-first style frontier. the tradeoff is that it visits the earlier levels again during every iteration.

## measurements

the program reports these values for every search:

- `depth`: number of moves in the final path
- `cost`: sum of the costs for cells entered by the path
- `expanded`: states whose neighbors were checked
- `generated`: states accepted into a frontier, including the start state
- `max frontier`: largest frontier during the search, used as a space measurement
- `iterations`: number of depth limits used by iddfs
- `time (ms)`: actual search time in milliseconds

`max frontier` is a simple machine-independent space comparison. it is not the exact number of bytes used by python.

## time and space complexity

for a finite graph, `V` is the number of open cells, `E` is the number of road connections, `b` is the branching factor, and `d` is the shallowest goal depth.

| algorithm | time | space | complete | optimal |
| --- | --- | --- | --- | --- |
| bfs | `O(V + E)` | `O(V)` | yes | fewest moves |
| dfs | `O(V + E)` | `O(V)` with visited cells | yes on this finite grid | no |
| ucs | `O((V + E) log V)` | `O(V + E)` | yes with positive costs | lowest cost |
| iddfs | about `O(b^d)` | much smaller frontier than bfs in the usual tree case | yes | fewest moves |

## example comparison

this is one run with python 3.12.5 using this command:

```bash
python3 main.py --rows 8 --cols 8 --obstacles 0.25 --seed 4800 --hide-paths
```

| algorithm | depth | cost | expanded | generated | max frontier | iterations | example time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bfs | 14 | 88 | 50 | 51 | 7 | 1 | 0.140 ms |
| dfs | 14 | 88 | 20 | 28 | 8 | 1 | 0.108 ms |
| ucs | 14 | 49 | 45 | 51 | 11 | 1 | 0.221 ms |
| iddfs | 14 | 88 | 381 | 389 | 8 | 15 | 1.159 ms |

execution time changes between computers and runs, but the other values stay the same when the seed and settings stay the same.

in this example, bfs and iddfs found a shallow path with 14 moves. ucs also used 14 moves, but it chose different cells and lowered the cost from 88 to 49. dfs happened to reach the goal after fewer expansions on this map, but that does not make dfs optimal. iddfs expanded the most states because it repeated the lower depth levels 15 times.

## conclusion

bfs is a good choice when every move has the same importance and the goal should be reached in the fewest moves. dfs can reach a solution quickly depending on neighbor order, but its path quality is not guaranteed. ucs is the best choice for this weighted navigation problem when travel cost matters. iddfs is useful when the goal depth is unknown and a shallow solution is needed, but its repeated work can make it slower.

## tests

run all tests with:

```bash
python3 -m unittest discover -v
```

the tests check shortest paths, lowest-cost paths, unreachable maps, start equal to goal, invalid input, random seed repeatability, depth limits, command-line output, and the reported measurements.

## project files

```text
main.py
src/uninformed_search/grid.py
src/uninformed_search/models.py
src/uninformed_search/comparison.py
src/uninformed_search/algorithms/bfs.py
src/uninformed_search/algorithms/dfs.py
src/uninformed_search/algorithms/ucs.py
src/uninformed_search/algorithms/iterative_deepening.py
tests/test_search.py
tests/test_grid.py
tests/test_main.py
```

## resources

- https://www.geeksforgeeks.org/difference-between-informed-and-uninformed-search-in-ai/
- https://www.geeksforgeeks.org/search-algorithms-in-ai/
