import glob
import os
import pickle
# class for a Pentomino object holds the relative positions of every space 
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
    def __init__(self, grid_size, pentomino_size=5):
        self.G = grid_size
        self.S = pentomino_size # 5 by default, don't think it will change
        self.O = [0] # position variable offsets
        self.N = 1e9 # obvious dummy value for number of pentominos

    def map_variables(self, list_of_pos_lists):
       
        # number of pentominos
        self.N = len(list_of_pos_lists) 

        # position offset for each pentomino
        for pentomino_pos_list in list_of_pos_lists:
            self.O.append(self.O[-1] + len(pentomino_pos_list))
        
        # total number of positions
        self.T = self.O[-1]
        
        # # set next available to the first id after the placement ids
        # self.next_available = len(list_of_pos_lists) * self.grid_size + 1

        # # for each pentomino:
        # for (i, pos_list) in enumerate(list_of_pos_lists):

        #     # set the starting clause id for that pentomino
        #     self.starting_clause_ids.append(self.next_available)

        #     # # for each possible pentomino position in the list of positions
        #     # # for the given pentomino:
        #     # for (j, pos_set) in enumerate(pos_list):

        #     #     # global clause_variable is the next available (current offset) 
        #     #     # plus the index of the current pos in the list of positions
        #     #     clause_var = self.next_available + j
        #     #     for (k, )

        #     #     # gonna need one more loop
        #     #     pos_var = self.get_num_placement(pos, i)
        #     #     s += f"-{clause_var} {pos_var}\n"
        #     #     s += f"{self.next_available + j}"
        #     self.next_available += len(pos_list)
        # self.starting_total_id = self.next_available

    # get the ID of an assignment variable for a given pentomino and space
    def get_num_assignment(self, pentomino_index, space_index):
        return self.G * pentomino_index + space_index + 1
    
    # get the ID of an exclusivity variable for a given pentomino and space
    def get_num_exclusivity(self, pentomino_index, space_index):
        return self.G * (self.N + pentomino_index) + space_index + 1
    
    def get_num_position(self, pentomino_index, position_index):
        return 2 * self.G * self.N + self.O[pentomino_index] + position_index + 1

    def get_num_pos_set(self, pentomino_index):
        return 2 * self.G * self.N + self.T + pentomino_index + 1

    def build_clause(self, id_list):
        return ' '.join([str(x) for x in id_list]) + ' 0\n'
    
    def get_assignment_from_num(self, num):
        pos = (num - 1) % self.G
        pent = (num - 1) // self.G
        return (pent, pos)

    def generate_printout(self, list_of_pos_lists):
        # DIMAC CNF header: "p cnf <num of vars> <num of clauses>"
        s = f"p cnf {self.N * (2 * self.G + 1) + self.T} {self.T * (self.S + 2) + 2 * self.N + self.G * (self.N**2 + self.N + 1)}\n"
        
        # permutation definition
        for pentomino in range(self.N):

            # ACP block
            for pos_id in range(len(list_of_pos_lists[pentomino])):
                
                # PIA expression
                aip_clause_ids = []
                position = self.get_num_position(pentomino, pos_id)

                for tile in list_of_pos_lists[pentomino][pos_id]:
                    
                    # PIA component (~Pa1 v A1)
                    assignment = self.get_num_assignment(pentomino, tile)
                    s += self.build_clause([-position, assignment])

                    # add assignment literals to aip clause list for later
                    aip_clause_ids.append(-assignment)

                # AIP clause (Pa1 v ~A1 v ~A2 v ~A4 v ~A7 v ~A8)
                s += self.build_clause([position] + aip_clause_ids)

            # PIS expression
            sip_clause_ids = []
            pos_set = self.get_num_pos_set(pentomino)

            for pos_id in range(len(list_of_pos_lists[pentomino])):   

                # PIS component (Sa v ~Pa1)
                position = self.get_num_position(pentomino, pos_id)
                s += self.build_clause([pos_set, -position])

                # add position literals to sip clause list for later
                sip_clause_ids.append(position)

            # SIP clause (~Sa v Pa1 v Pa2 v Pa3 v Pa4 v Pa5 v Pa6 v Pa7 v Pa8)
            s += self.build_clause([-pos_set] + sip_clause_ids)

            # set requirement clause (Sa)
            s += self.build_clause([pos_set])
        
        # grid definition
        for space in range(self.G):

            # exclusivity block
            occupancy_clause_ids = []

            for exclusivity_pentomino in range(self.N):

                # EIA expression
                aie_clause_ids = []
                exclusivity = self.get_num_exclusivity(exclusivity_pentomino, space)

                for assignment_pentomino in range(self.N):
                        
                    # EIA component (~EaS1 v A1) or (~EaS1 v ~B1)
                    assignment = -self.get_num_assignment(assignment_pentomino, space)
                    if assignment_pentomino == exclusivity_pentomino:
                        # remember that the assignment variable is negated if it's space
                        # NOT the same as the exclusivity variable's space, and vice versa
                        assignment = -assignment 
                    s += self.build_clause([-exclusivity, assignment])

                    # add assignment literals to aie clause list for later
                    aie_clause_ids.append(-assignment)

                # AIE clause (EaS1 v ~A1 v B1)
                s += self.build_clause([exclusivity] + aie_clause_ids)

                # add exclusivity literals to occupancy clause list for later
                occupancy_clause_ids.append(exclusivity)

            # occupancy clause (EaS1 v EbS1)
            s += self.build_clause(occupancy_clause_ids)

        # # all pentominos need a valid assignment
        # # for each pentomino, look at it's list of position sets
        # for (i, pos_sets) in enumerate(list_of_pos_lists):
            
        #     # for each list of position sets, look at each position set
        #     print("POS_SETS = ", pos_sets)
        #     for (j, pos_set) in enumerate(pos_sets):
                
        #         # get the clause var corresponding to the current pentomino
        #         # and position set id
        #         clause_var = self.get_num_clause(j, i)

        #         # for each position in the position set
        #         for pos in pos_set:
        #             # get the placement var corresponding to the current
        #             # pentomino and local position id
        #             pos_var = self.get_num_placement(pos, i)

        #             # add the position term to the string
        #             s += f"-{clause_var} {pos_var} 0\n"

        #         # add the clause term to the string
        #         s += f"{clause_var} 0\n"

        # for (i, pos_sets) in enumerate(list_of_pos_lists):
        #     pentomino_var = self.get_num_total(i)
        #     for (j, pos_set) in enumerate(pos_sets):
        #         clause_var = self.get_num_clause(j, i)
        #         s += f"{pentomino_var} -{clause_var} 0\n"

        # for (i, pos_sets) in enumerate(list_of_pos_lists):
        #     pentomino_var = self.get_num_total(i)
        #     s += f"{pentomino_var} 0\n"

        # # need condition for no two pentominos in the same position
        # for grid_index in range(self.grid_size):
        #     for pent_index in range(len(list_of_pos_lists)):
        #         for pent_index_2 in range(len(list_of_pos_lists)):
        #             if pent_index != pent_index_2:
        #                 s += 

        return s
    

if __name__ == "__main__":
    pentomino_pathnames = glob.glob("pentominos/*")
    print(pentomino_pathnames)
    pentominos = [Pentomino(f) for f in pentomino_pathnames][0:18]
    # print(pentominos)
    suffix = "1"
    grid = Grid(f"grids/grid{suffix}.txt")
    # print(grid.get_valid_position_lists(pentominos[0]))

    m = Mapper(grid.size)
    list_of_pos_lists = [grid.get_valid_position_lists(pentominos[i]) for i in range(len(pentominos))]
    combos = 1
    sum = 0
    for (i, pos_list) in enumerate(list_of_pos_lists):
        print(i, len(pos_list))
        combos *= len(pos_list)
        sum += len(pos_list)
    print(combos)
    print(sum)

    m.map_variables(list_of_pos_lists)
    s = m.generate_printout(list_of_pos_lists)

    output_filename = f'output{suffix}.cnf'
    output = open(output_filename, 'w')
    output.write(s)
    pickle.dump(m, open(f'mapper{suffix}.pkl', 'wb'))
    # output.write(f"c {output_filename}\np cnf {variables} {clauses}\n")

    
# grid1
# 4 duodecillion :(
# 4 699 325 490 484 678 553 289 281 643 492 523 015 680

# grid5x15 (3211s)
# 91 nonillion
# 91 228 306 732 639 680 489 536 524 124 160

# grid5x16 (7603s)
# 56 decillion
# 56 975 008 705 871 680 574 389 141 584 740 352

# grid5x17 (???)
# 31 undecillion
# 31 326 899 301 583 863 803 055 754 444 800 000 000
