#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <unordered_map>
#include <utility>
using namespace std;

// These structs are needed to use std::pair as a key in an unordered_map
// Define a hash function for std::pair
struct pair_hash {
    template <class T1, class T2>
    std::size_t operator () (const std::pair<T1, T2> &p) const {
        auto hash1 = std::hash<T1>{}(p.first);
        auto hash2 = std::hash<T2>{}(p.second);
        return hash1 ^ hash2; // Combine the hash values
    }
};

// Define an equality function for std::pair
struct pair_equal {
    template <class T1, class T2>
    bool operator () (const std::pair<T1, T2> &p1, const std::pair<T1, T2> &p2) const {
        return p1.first == p2.first && p1.second == p2.second;
    }
};

class Pentomino {
private:
    vector<vector<int>> shape;
    int rotations;
public:
    // create a pentomino from a shape and number of rotations
    Pentomino(vector<vector<int>> shape, int rotations) {
        this->shape = shape;
        this->rotations = rotations;
    }
    // create a pentomino by reading from a properly formatted file
    Pentomino(string filename) {
        ifstream file(filename);
        string line;
        getline(file, line);
        this->rotations = stoi(line);
        while (getline(file, line)) {
            int space = line.find(' ');
            this->shape.push_back({stoi(line.substr(0, space)), stoi(line.substr(space + 1))});
        }
    }
    vector<vector<int>> get_shape() {
        return shape;
    }
    int get_num_rotations() {
        return rotations;
    }
    // return a string representation of the pentomino which reports a base position and the number of rotations
    string to_string() {
        string str = "[";
        for (int i = 0; i < shape.size(); i++) {
            str += "(" + std::to_string(shape[i][0]) + ", " + std::to_string(shape[i][1]) + "), ";
        }
        str = str.substr(0, str.size() - 2);
        str += "] x " + std::to_string(rotations) + "r";
        return str;
    }
    // return a list of all possible rotations of a pentomino centered at a given position
    vector<vector<vector<int>>> get_positions(vector<int> center) {
        vector<vector<vector<int>>> positions;
        int cx = center[0];
        int cy = center[1];

        // go through all of a pentomino's rotations
        for (int i = 0; i < rotations; i++) {
            // map the rotated shape to the grid position so that pentomino (0, 0) is at the given center
            vector<vector<int>> position;
            for (int j = 0; j < shape.size(); j++) {
                int dx = shape[j][0];
                int dy = shape[j][1];
                // cout << "dx = " << dx << ", dy = " << dy << endl;
                if (i == 0) { // no rotation
                    position.push_back({cx+dx, cy+dy});
                }
                else if (i == 1) { // 90 degree rotation
                    position.push_back({cx-dy, cy+dx});
                }
                else if (i == 2) { // 180 degree rotation
                    position.push_back({cx-dx, cy-dy});
                }
                else { //i == 3: 270 degree rotation
                    position.push_back({cx+dy, cy-dx});
                }
            }
            positions.push_back(position);
        }
        return positions;
    }
};

class Grid {
private:
    vector<vector<int>> grid;
    unordered_map<int, pair<int, int>> index_to_position;
    unordered_map<pair<int, int>, int, pair_hash, pair_equal> position_to_index;
public:
    // read in a grid line-by-line from a properly formatted file until there's no input left
    Grid(string filename) {
        ifstream file(filename);
        string line;
        int i = 1;
        while (getline(file, line)) {
            int space = line.find(' ');
            int x = stoi(line.substr(0, space));
            int y = stoi(line.substr(space + 1));
            this->grid.push_back({x, y});
            this->index_to_position.insert({i, {x, y}});
            this->position_to_index.insert({make_pair(x, y), i});
            i++;
        }
    }

    vector<vector<int>> get_grid() {
        return grid;
    }

    // check if a list of positions is valid by checking if each position is in the grid
    bool is_valid(vector<vector<int>> position) {
        for (int i = 0; i < position.size(); i++) {
            if (position_to_index.find(make_pair(position[i][0], position[i][1])) == position_to_index.end()) {
                return false;
            }
        }
        return true;
    }
    
    // get the valid positions of a supplied pentomino in the grid
    // iterate through the grid and try placing the center of the pentomino at each point
    // if the pentomino fits, add it to the position list, using the mappings to indices.
    vector<vector<int>> get_valid_positions(Pentomino pentomino) {
        vector<vector<int>> valid_positions;
        for (int i = 0; i < grid.size(); i++) {

            // get all the possible positions of the pentomino centered at each grid position
            vector<vector<vector<int>>> positions = pentomino.get_positions(grid[i]);

            // go through each position. if it's valid, then map it to indices and add it to the list of valid positions
            for (int j = 0; j < positions.size(); j++) {
                if (is_valid(positions[j])) {
                    vector<int> mapped_position;
                    for (int k = 0; k < positions[j].size(); k++) {
                        mapped_position.push_back(position_to_index.at({positions[j][k][0], positions[j][k][1]}));
                    }
                    valid_positions.push_back(mapped_position);
                }
            }
        }
        return valid_positions;
    }
};

// read in all the pentominoes in a folder
vector<Pentomino> read_pentominoes(string filename, int num_pentominoes) {
    vector<Pentomino> pentominoes;
    string path = "./pentominos";
    for (/*const*/ auto & entry : filesystem::directory_iterator(path))
        pentominoes.push_back(Pentomino(entry.path()));

    vector<Pentomino> trimmed;
    for (int i = 0; i < num_pentominoes; i++) {
        trimmed.push_back(pentominoes[i]);
    }
    return trimmed;
}

// map a list of positions to an efficient representation for a single pentomino
// the efficient representation is a list of long longs, where each long long represents 64 grid positions
// that way in a couple numbers you can check if two positions overlap by checking if the bitwise AND of the two numbers is 0
vector<vector<long long>> map_1p_positions_to_efficient(vector<vector<int>> positions, int grid_size) {
    // we need ceil(grid_size / 64) long longs to represent the grid
    int required_long_longs = (grid_size + 63) / 64; 
    vector<vector<long long>> efficient_positions;

    // for each position, make a long long for each 64 grid positions. 
    // set the bit at the index of the grid position to 1
    for (int i = 0; i < positions.size(); i++) { 
        vector<long long> efficient_position(required_long_longs, 0);
        for (int j = 0; j < positions[i].size(); j++) {
            int index = positions[i][j];
            efficient_position[index / 64] |= 1 << (index % 64);
        }
        efficient_positions.push_back(efficient_position);
    }
    return efficient_positions;
}

// map a list of positions to an efficient representation for multiple pentominoes
// just call the 1p version for each pentomino and append and return all the results
vector<vector<vector<long long>>> map_allp_positions_to_efficient(vector<vector<vector<int>>> positions, int grid_size) {
    vector<vector<vector<long long>>> efficient_positions;
    for (int i = 0; i < positions.size(); i++) {
        efficient_positions.push_back(map_1p_positions_to_efficient(positions[i], grid_size));
    }
    return efficient_positions;
}

// check if two efficient representations of pentomino positions overlap
// if a single pair of long longs AND together to 1, then they have a position in common, so return true
// if they all AND together to 0, then they have no positions in common, so return false
bool overlap(vector<long long>& a, vector<long long>& b) {
    if (a.size() != b.size()) {
        cout << "Error: trying to compare two efficient positions of different sizes" << endl;
        return false;
    }
    for (int i = 0; i < a.size(); i++) {
        if (a[i] & b[i]) {
            return true;
        }
    }
    return false;
}

void assign(vector<long long>& existing, vector<long long>& next) {
    for (int i = 0; i < existing.size(); i++) {
        existing[i] |= next[i];
    }
}

void unassign(vector<long long>& existing, vector<long long>& next) {
    for (int i = 0; i < existing.size(); i++) {
        existing[i] &= ~next[i];
    }
}

string vector_to_string(vector<long long>& v) {
    string str = "[";
    for (int i = 0; i < v.size(); i++) {
        str += std::to_string(v[i]) + ", ";
    }
    str = str.substr(0, str.size() - 2);
    str += "]";
    return str;
}

string format_positions(vector<int>& indices, vector<vector<vector<long long>>>& all_valid_positions) {
    string str = "";
    for (int i = 0; i < indices.size(); i++) {
        str += vector_to_string(all_valid_positions[i][indices[i]]) + "\n";
    }
    return str;
}

int main() {
    int size = 5;
    Grid grid("grids/grid5x10.txt");
    if (grid.get_grid().size() % size != 0) {
        cout << "Invalid grid size: pentominoes of size " << size << " don't evenly fill a grid of size " << grid.get_grid().size() << endl;
        return 1;
    }
    int num_pentominoes = grid.get_grid().size() / size;
    for (int i = 0; i < grid.get_grid().size(); i++) {
        cout << grid.get_grid()[i][0] << " " << grid.get_grid()[i][1] << endl;
    }

    vector<Pentomino> pentominoes = read_pentominoes("pentominos", num_pentominoes);
    for (int i = 0; i < pentominoes.size(); i++) {
        cout << pentominoes[i].to_string() << endl;
    }

    vector<vector<vector<int>>> all_valid_positions;
    for (int i = 0; i < pentominoes.size(); i++) {
        vector<vector<int>> valid_positions = grid.get_valid_positions(pentominoes[i]);
        all_valid_positions.push_back(valid_positions);
        // cout << "Pentomino " << i << " has " << valid_positions.size() << " valid positions" << endl;
    }

    // // print out pentomino positions
    // for (int i = 0; i < all_valid_positions.size(); i++) {

    //     // for each pentomino
    //     cout << "Pentomino " << i << endl;
    //     cout << all_valid_positions[i].size() << " valid positions" << endl;
    //     for (int j = 0; j < all_valid_positions[i].size(); j++) {

    //         // for each position
    //         cout << "  ";
    //         for (int k = 0; k < all_valid_positions[i][j].size(); k++) {
    //             cout << all_valid_positions[i][j][k] << " ";
    //         }
    //         cout << endl;
    //     }
    // }

    // map all the positions to efficient representations
    vector<vector<vector<long long>>> all_efficient_positions = map_allp_positions_to_efficient(all_valid_positions, grid.get_grid().size());

    // find an efficient solution:
    // for each pentomino, try each position
    int current = 0;
    int i = 0;
    vector<int> position_counts(num_pentominoes);
    for (int i = 0; i < position_counts.size(); i++) {
        position_counts[i] = all_efficient_positions[i].size();
    }
    vector<int> current_indices(num_pentominoes, 0);
    vector<long long> current_assignments((grid.get_grid().size() + 63) / 64, 0);

    while (true) {
        if (current_indices[current] == position_counts[current]) {
            current_indices[current] = 0;
            current--;
            if (current == -1) {
                cout << "Done" << endl;
                return 0;
            }
            unassign(current_assignments, all_efficient_positions[current][current_indices[current]]);
            current_indices[current]++;
            continue;
        }
        vector<long long> pos = all_efficient_positions[current][current_indices[current]];
        // if there's an overlap, try the next position
        if (overlap(current_assignments, pos)) {
            current_indices[current]++;
        }
        else {
            assign(current_assignments, pos);
            current++;
            if (current == num_pentominoes) {
                cout << "Solution found! Positions are:\n" << format_positions(current_indices, all_efficient_positions) << endl;
                return 0;
            }
        }
        if (i % 100000 == 0) {
            cout << i << ": current = " << current << ", current_indices = ";
            for (int j = 0; j < current_indices.size(); j++) {
                cout << current_indices[j] << " ";
            }
            cout << endl;
        }
        i++;
    }



    return 0;
}