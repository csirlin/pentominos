#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
using namespace std;

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
    int get_rotations() {
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
};

class Grid {
private:
    vector<vector<int>> grid;
public:
    Grid(vector<vector<int>> grid) {
        this->grid = grid;
    }
    // read in a grid line-by-line until there's no input left
    Grid(string filename) {
        ifstream file(filename);
        string line;
        while (getline(file, line)) {
            int space = line.find(' ');
            this->grid.push_back({stoi(line.substr(0, space)), stoi(line.substr(space + 1))});
        }
    }
    vector<vector<int>> get_grid() {
        return grid;
    }
};

// read in all the pentominoes in a folder
vector<Pentomino> read_pentominoes(string filename) {
    vector<Pentomino> pentominoes;
    string path = "./pentominos";
    for (/*const*/ auto & entry : filesystem::directory_iterator(path))
        pentominoes.push_back(Pentomino(entry.path()));

    return pentominoes;
}

// #include <string>
// #include <iostream>
// #include <filesystem>
// namespace fs = std::filesystem;

// int main()
// {
//     std::string path = "/path/to/directory";
//     for (const auto & entry : fs::directory_iterator(path))
//         std::cout << entry.path() << std::endl;
// }

int main() {
    int size = 5;
    Grid grid("grids/grid1.txt");
    if (grid.get_grid().size() % size != 0) {
        cout << "Invalid grid size: pentominoes of size " << size << " don't evenly fill a grid of size " << grid.get_grid().size() << endl;
        return 1;
    }
    int num_pentominoes = grid.get_grid().size() / size;
    for (int i = 0; i < grid.get_grid().size(); i++) {
        cout << grid.get_grid()[i][0] << " " << grid.get_grid()[i][1] << endl;
    }

    vector<Pentomino> pentominoes = read_pentominoes("pentominos");
    for (int i = 0; i < pentominoes.size(); i++) {
        cout << pentominoes[i].to_string() << endl;
    }

    return 0;
}