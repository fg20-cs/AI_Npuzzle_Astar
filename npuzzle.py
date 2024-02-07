import sys
import numpy as np

inputs_count = len(sys.argv)

if inputs_count != 2:
  print("Error: Provide the path to the file containing the values of the maze!")
  print("Usage example: python project1.py <path_to_the_maze_file>")
  sys.exit()
file_name = sys.argv[-1]

# function to print a maze
def print_maze(maze):
  for row in maze:
    for el in row:
      if(el == 0):
        print("-\t", end='')
      else:
        print(el, "\t", end='')
    print("")

#func to get the contents of the file
def read_maze(file_input):
  ints = []
  with open(file_input, "r") as file:
    for line in file:
      ints.append([int(x) for x in line.split()])
  return ints

def get_goal_state(initial_state):
  x = []
  n = 0
  for row in initial_state:
    n+=1
    for e in row:
      x.append(e)
  x.sort()
  goal_state = []
  for r in range(0, len(x), n): 
    temp = []
    for i in range(n):
      temp.append(x[i+r])
    goal_state.append(temp)
  return goal_state

class State:

  def __init__(self, data, f_score, depth):
    self.data = data
    self.depth = depth
    self.f = f_score
    self.parent = None

  def generate_next_states(self):
    x_blanc, y_blanc = self.find(0)
    movements = [[x_blanc-1, y_blanc], [x_blanc+1, y_blanc], [x_blanc, y_blanc-1], [x_blanc, y_blanc+1]]
    new_states = []
    for movement in movements:
      new_state_data = self.move(x_blanc, y_blanc, movement[0], movement[1])
      if new_state_data is not None:
        new_state = State(new_state_data, 0, self.depth+1)
        new_states.append(new_state)
    return new_states

  def move(self, x1, y1, x2, y2):
    if x2 >= 0 and x2 < len(self.data) and y2 >= 0 and y2 < len(self.data):
      temp_data = []
      temp = self.copy()
      temp_data = temp.data
      temp_data[x2][y2], temp_data[x1][y1] = temp_data[x1][y1], temp_data[x2][y2]
      return temp_data
    else:
      return None
    
  #CH
  def copy(self):
    temp = State([], self.f, self.depth)
    temp.parent = self.parent
    for i in self.data:
      t = []
      for j in i:
        t.append(j)
      temp.data.append(t)
    return temp

  def find(self, x):
    for i in range(len(self.data)):
      for j in range(len(self.data)):
        if self.data[i][j] == x:
          return i, j

class Maze:

  def __init__(self, init_state_data, goal_state_data):
    self.n = len(init_state_data)
    self.open = []
    self.closed = []
    self.solution = []
    self.init_state_data = init_state_data
    self.goal_state_data = goal_state_data

  def manhattan_dist(self, x_state, y_state, x_goal, y_goal):
    return abs(x_state-x_goal) + abs(y_state-y_goal)
        
  def h_score(self, start_state):
    h = 0
    for i in range(self.n):
      for j in range(self.n):
        x_goal = int(start_state.data[i][j] / self.n)
        y_goal = self.goal_state_data[x_goal].index(start_state.data[i][j])
        h += self.manhattan_dist(i, j, x_goal, y_goal)
    return h

  def f_score(self, current_state):
    return self.h_score(current_state) + current_state.depth
  
  def comparator(self, state_1, state_2):
    return self.f_score(state_1) - self.f_score(state_2)
  
  def is_equal_states(self, state_1_data, state_2_data):
    for i in range(self.n):
      for j in range(self.n):
        if state_1_data.data[i][j] != state_2_data.data[i][j]:
          return False
    return True
  
  def find_state(self, curr_state, state_list):
    for state in state_list:
      if self.is_equal_states(curr_state, state):
        return state
    return None


  # generates the path to a solution using A* algorithm
  def solve_with_A_star(self):

    start_state = State(self.init_state_data, 0, 0)
    start_state.f = self.h_score(start_state) + start_state.depth
    self.open.append(start_state)

    while len(self.open) != 0:

      current_state = self.open[0]
     
      if self.h_score(current_state) == 0:
        state = current_state.copy()
        self.solution.append(state)
        while state.parent is not None:
          state = state.parent
          self.solution.append(state.copy())
        break

      del self.open[0]
      self.closed.append(current_state)

      new_states = current_state.generate_next_states()
        
      for state in new_states:
        if self.find_state(state, self.closed) is not None:
          continue

        if self.find_state(state, self.open) is None:
          self.open.append(state)
        else:
          found_state = self.find_state(state, self.open)
          if state.depth >= found_state.depth:
            continue

        state.f = self.f_score(state)
        state.parent = current_state
      
      from functools import cmp_to_key
      self.open.sort(key=cmp_to_key(self.comparator), reverse=False)

  def empty_open_list(self):
    for _ in range(len(self.open)):
      del self.open[0]


maze = read_maze(file_name)
n = len(maze)
goal_state = get_goal_state(maze)

game = Maze(maze, goal_state)
game.solve_with_A_star()

closed_list_len = len(game.closed)
open_list_len = len(game.open)

print("start state: ")
print_maze(game.init_state_data)
print("\ngoal state: ")
print_maze(game.goal_state_data)


print("\nSteps taken: ")

game.solution.reverse()
for i in range(len(game.solution)):
  print("F_score: ", game.solution[i].f)
  print_maze(game.solution[i].data)
  print("\n\n")

print("Number of moves to reach goal state: ", end="")
print(len(game.solution)-1, "moves\n")