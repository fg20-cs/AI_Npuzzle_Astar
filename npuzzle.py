import sys
import time

#making sure that the path to file containing the puzzle is provided
inputs_count = len(sys.argv)
if inputs_count != 2:
  print("Error: Provide the path to the file containing the values of the maze!")
  print("Usage example: python project1.py <path_to_the_maze_file>")
  sys.exit()
file_name = sys.argv[-1]


#function to get the contents of the file
# ACCEPTS: file_input - path to the file that contains the data about the initial state
# RETURNS: a 2D array that contains data of the state
def read_from_file(file_input):
  ints = []
  with open(file_input, "r") as file:
    for line in file:
      ints.append([int(x) for x in line.split()])
  return ints

#function to generate the goal state from the provided initial state
# ACCEPTS: a State object of the initial state
# RETURNS: a 2D array that contains data of the goal state
def generate_goal_state(initial_state):
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


#class representing a single state of the puzzle
class State:

  def __init__(self, data, f_score, depth):
    self.data = data
    self.depth = depth
    self.f_score = f_score
    self.parent = None

  #function to print the state of the puzzle
  # ACCEPTS: -
  # RETURNS: -
  def print_state(self):
    for row in self.data:
      for el in row:
        if(el == 0): print("-\t", end='')
        else: print(el, "\t", end='')
      print("")

  #function to expand the state / generates the child states
  # ACCEPTS: -
  # RETURNS: list of all possible child states generated from the current state
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

  #function that applies the provided movement to the state and makes sure the movement is within the borders of the puzzle
  # ACCEPTS: x1 - x coordinate of the start point 
  #          y1 - y coordinate of the start point 
  #          x2 - x coordinate of target point 
  #          y2 - y coordinate of target point 
  # RETURNS:
  #          if valid move, returns data of the newly generated state after applying the movement from (x1, y1) to (x2, y2)
  #          else returns None 
  def move(self, x1, y1, x2, y2):
    if x2 >= 0 and x2 < len(self.data) and y2 >= 0 and y2 < len(self.data):
      temp_data = []
      temp = self.copy()
      temp_data = temp.data
      temp_data[x2][y2], temp_data[x1][y1] = temp_data[x1][y1], temp_data[x2][y2]
      return temp_data
    else:
      return None
    
  #funciton to create a copy of a state
  # ACCEPTS: -
  # RETURNS: a copy of a State
  def copy(self):
    temp = State([], self.f_score, self.depth)
    temp.parent = self.parent
    for i in self.data:
      t = []
      for j in i:
        t.append(j)
      temp.data.append(t)
    return temp

  #funciton to find the location of the tile x in the state
  # ACCEPTS: value to be found on the maze of the state
  # RETURNS: (x, y) coordinates of the found element, else None
  def find(self, x):
    for i in range(len(self.data)):
      for j in range(len(self.data)):
        if self.data[i][j] == x:
          return i, j
    return None
        

# class that represents the Puzzle
class Puzzle:

  def __init__(self, init_state_data, goal_state_data):
    self.n = len(init_state_data)
    self.open = []
    self.closed = []                        
    self.solution = []                      #list containing the optimal solution
    self.init_state_data = init_state_data  #data of the initial state
    self.goal_state_data = goal_state_data  #data of the goal state

  #function to compute the manhattan distance between 2 states of a tile
  # ACCEPTS: x_state - x coordinate of a tile in the state
  #          y_state - y coordinate of a tile in the state
  #          x_goal  - x coordinate of a tile in the goal 
  #          y_goal  - y coordinate of a tile in the goal 
  # RETURNS: 
  #          the distance for a tile between some state and goal state
  def manhattan_dist(self, x_state, y_state, x_goal, y_goal):
    return abs(x_state-x_goal) + abs(y_state-y_goal)
        
  #fucntion to compute the overall heuristic score of the state using Manhattan distance
  #ACCEPTS: a State object
  #RETURNS: heuristic score for the state
  def h_score(self, start_state):
    h = 0
    for i in range(self.n):
      for j in range(self.n):
        x_goal = int(start_state.data[i][j] / self.n)
        y_goal = self.goal_state_data[x_goal].index(start_state.data[i][j])
        h += self.manhattan_dist(i, j, x_goal, y_goal)
    return h

  #function to compute the f_score for a state
  #ACCEPTS: a State object for current state
  #RETURNS: f_score value for the state
  def f_score(self, current_state):
    return self.h_score(current_state) + current_state.depth
  
  #fucntion to use for priority queue
  def comparator(self, state_1, state_2):
    return self.f_score(state_1) - self.f_score(state_2)
  
  #fucntion to compare two states
  #ACCEPTS: state_1_data - data on state_1, state_2_data - data on state_2
  #RETURNS: boolean - True if states are equal, False if states are not equal
  def is_equal_states(self, state_1_data, state_2_data):
    for i in range(self.n):
      for j in range(self.n):
        if state_1_data.data[i][j] != state_2_data.data[i][j]:
          return False
    return True
  
  #funciton to find a state in the list of states
  #ACCEPTS: curr_state - State object of the current state, state_list - list of State objects
  #RETURNS: State object containing the found state, else None
  def find_state(self, curr_state, state_list):
    for state in state_list:
      if self.is_equal_states(curr_state, state):
        return state
    return None


  #function to generate the path to a solution using A* algorithm
  #ACCEPTS: -
  #RETURNS: - (populates the solution list of the Puzzle object)
  def solve_with_A_star(self):

    start_state = State(self.init_state_data, 0, 0)
    start_state.f_score = self.h_score(start_state) + start_state.depth
    self.open.append(start_state)

    while len(self.open) != 0:

      current_state = self.open[0]
     
      #goal state is found
      if self.h_score(current_state) == 0:
        #retrace the path from goal state to inital state using the parents
        state = current_state.copy()
        self.solution.append(state)
        while state.parent is not None:
          state = state.parent
          self.solution.append(state.copy())
        break

      #remove current state from the list that serves as a prioriry queue
      del self.open[0]

      #add the state to the list of closed states
      self.closed.append(current_state)

      #generate all the possible children from the current state
      new_states = current_state.generate_next_states() 
      for state in new_states:
        #do nothing if the state is already in the closed list
        if self.find_state(state, self.closed) is not None:
          continue

        #add to open list for future expansion as state not found in the closed list 
        if self.find_state(state, self.open) is None:
          self.open.append(state)
        else:
          #makes sure that the found state is closest to the optimal path
          found_state = self.find_state(state, self.open)
          if state.depth >= found_state.depth:
            continue

        state.f_score = self.f_score(state)
        state.parent = current_state
      
      #sort the open list to make sure that the state with the smallest f_score is at the beginning of the list
      from functools import cmp_to_key
      self.open.sort(key=cmp_to_key(self.comparator), reverse=False)


# reading from the file
maze = read_from_file(file_name)
goal_state = generate_goal_state(maze)

#generating the Puzzle
game = Puzzle(maze, goal_state)

start_time = time.time()

game.solve_with_A_star()

end_time = time.time()

print("start state: ")
init_state = State(maze, 0, 0)
init_state.print_state()

print("\ngoal state: ")
goal_state = State(goal_state, 0, 0)
goal_state.print_state()

print("\nSteps taken: ")

game.solution.reverse()
for i in range(len(game.solution)):
  print("F_score: ", game.solution[i].f_score)
  game.solution[i].print_state()
  print("\n\n")

print("Number of moves to reach goal state: ", end="")
print(len(game.solution)-1, "moves\n")
print("Number of states in closed list: ", len(game.closed))
print("Time to reach goal state: ", end_time - start_time, " seconds")