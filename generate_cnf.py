import glob
import os
# class for a Pentomino object holds the relative positions of every cell 
# occupied by a pentomino and provides information about them to the caller
class Pentomino:

    # initialize with coordinate pairs of positions, and a number of rotations.
    # one of the positions must be the relative center at (0, 0). For example,
    # the T-shaped pentomino might be initialized as
    # t = Pentomino([(0, 0), (-1, 0), (1, 0), (0, -1), (0, -2)], 4)
    # and the + sign-shaped pentomino might be initialized as
    # p = Pentomino([(0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)], 1)
    def __init__(self, pentomino_filename):
        self.pairs = []
        with open(pentomino_filename, 'r') as file:
            pentomino_str = file.read()
            pentomino_list = pentomino_str.split('\n')
            for i in range(1, len(pentomino_list)):
                pair = tuple(pentomino_list[i].split(' '))
                pair = (int(pair[0]), int(pair[1]))
                self.pairs.append(pair)
        self.rotations = int(pentomino_list[0])

    # returns a list of lists of absolute positions of each cell in the
    # pentomino given the absolute position of the center. For example,
    # t.get_positions((5, 4)) would return something like 
    # [ [(5, 4), (4, 4), (6, 4), (5, 3), (5, 2)],
    #   [(5, 4), (5, 5), (5, 3), (6, 4), (7, 4)],
    #   [(5, 4), (6, 4), (4, 4), (5, 5), (5, 6)],
    #   [(5, 4), (5, 5), (5, 3), (4, 4), (3, 4)] ]
    def get_positions(self, center):
        positions = []
        for r in range(self.rotations):
            single_rot_positions = []
            (cx, cy) = center
            for (x, y) in self.pairs:
                if r == 0:
                    single_rot_positions.append((cx+x, cy+y))
                if r == 1:
                    single_rot_positions.append((cx-y, cy+x))
                if r == 2:
                    single_rot_positions.append((cx-x, cy-y))
                if r == 3:
                    single_rot_positions.append((cx+y, cy-x))
            positions.append(single_rot_positions)
        return positions

# class for a Grid - collection of coordinate pairs that the pentominos fit on
class Grid:

    # read in the list of coordinate pairs from a text file formatted as
    # x0 y0\nx1 y1\nx2 y2\n... into a dictionary and record the number of pairs
    def __init__(self, coordinate_filename):
        # read in from coordinate_file and store in the coordinate list
        self.coordinate_pairs = {}
        self.reverse_map = {}
        self.size = 0
        with open(coordinate_filename, 'r') as file:
            coordinate_str = file.read()
            coordinate_list = coordinate_str.split('\n')
            for i in range(len(coordinate_list)):
                pair = tuple(coordinate_list[i].split(' '))
                pair = (int(pair[0]), int(pair[1]))
                self.coordinate_pairs[pair] = self.size
                self.reverse_map[self.size] = pair
                self.size += 1

    # return true if all coordinate pairs in positions are in the grid
    def is_valid(self, positions):
        for pos in positions:
            if pos not in self.coordinate_pairs:
                return False
        return True
    
    # given a pentomino, try placing its center at every point in the grid
    # at all it's unique rotations and return a list of all the sets of position
    # ids that work for it.
    def get_valid_position_lists(self, pentomino):
        position_id_lists = []
        for center_pos in self.coordinate_pairs.keys():
            position_sets = pentomino.get_positions(center_pos)
            for pset in position_sets:
                if self.is_valid(pset):
                    position_id_lists.append([self.coordinate_pairs[p] for p in pset])
        return position_id_lists
    
    # returns a mapping from id 
    def get_mapping(self):
        return self.reverse_map

# map local id's to global id's for cnf format
class Mapper:
    def __init__(self, grid_size):
        self.next_available = 0
        self.grid_size = grid_size
        self.starting_clause_ids = []
        self.starting_total_id = -1

    def map_variables(self, list_of_pos_lists):
        
        # set next available to the first id after the placement ids
        self.next_available = len(list_of_pos_lists) * self.grid_size + 1

        # for each pentomino:
        for (i, pos_list) in enumerate(list_of_pos_lists):

            # set the starting clause id for that pentomino
            self.starting_clause_ids.append(self.next_available)

            # # for each possible pentomino position in the list of positions
            # # for the given pentomino:
            # for (j, pos_set) in enumerate(pos_list):

            #     # global clause_variable is the next available (current offset) 
            #     # plus the index of the current pos in the list of positions
            #     clause_var = self.next_available + j
            #     for (k, )

            #     # gonna need one more loop
            #     pos_var = self.get_num_placement(pos, i)
            #     s += f"-{clause_var} {pos_var}\n"
            #     s += f"{self.next_available + j}"
            self.next_available += len(pos_list)
        self.starting_total_id = self.next_available

    def get_num_placement(self, grid_index, pentomino_index):
        return pentomino_index * self.grid_size + grid_index + 1

    def get_num_clause(self, clause_index, pentomino_index):
        return self.starting_clause_ids[pentomino_index] + clause_index

    def get_num_total(self, pentomino_index):
        return self.starting_total_id + pentomino_index

    def generate_printout(self, list_of_pos_lists):
        
        s = "p cnf <num of vars> <num of clauses>\n"

        # all pentominos need a valid assignment
        # for each pentomino, look at it's list of position sets
        for (i, pos_sets) in enumerate(list_of_pos_lists):
            
            # for each list of position sets, look at each position set
            print("POS_SETS = ", pos_sets)
            for (j, pos_set) in enumerate(pos_sets):
                
                # get the clause var corresponding to the current pentomino
                # and position set id
                clause_var = self.get_num_clause(j, i)

                # for each position in the position set
                for pos in pos_set:
                    # get the placement var corresponding to the current
                    # pentomino and local position id
                    pos_var = self.get_num_placement(pos, i)

                    # add the position term to the string
                    s += f"-{clause_var} {pos_var} 0\n"

                # add the clause term to the string
                s += f"{clause_var} 0\n"

        for (i, pos_sets) in enumerate(list_of_pos_lists):
            pentomino_var = self.get_num_total(i)
            for (j, pos_set) in enumerate(pos_sets):
                clause_var = self.get_num_clause(j, i)
                s += f"{pentomino_var} -{clause_var} 0\n"

        for (i, pos_sets) in enumerate(list_of_pos_lists):
            pentomino_var = self.get_num_total(i)
            s += f"{pentomino_var} 0\n"

        # need condition for no two pentominos in the same position
        for gs in range(self.grid_size):
            for pent_index in range(len(list_of_pos_lists)):
                for pent_index_2 in range(len(list_of_pos_lists)):
                    if pent_index != pent_index_2:
                        s += 

        return s
    


pentomino_pathnames = glob.glob("pentominos/*")
pentominos = [Pentomino(f) for f in pentomino_pathnames]
grid = Grid("grids/grid1.txt")
print(grid.get_valid_position_lists(pentominos[0]))

m = Mapper(grid.size)
list_of_pos_lists = [grid.get_valid_position_lists(pentominos[i]) for i in range(len(pentominos))]
print(list_of_pos_lists)
m.map_variables(list_of_pos_lists)
s = m.generate_printout(list_of_pos_lists)

output_filename = 'output.cnf'
output = open(output_filename, 'w')
output.write(s)
# output.write(f"c {output_filename}\np cnf {variables} {clauses}\n")

    


