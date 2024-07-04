#include <iostream>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

// read in grid
// read in a file line-by-line until there's no input left
vector<vector<int>> read_grid(string filename) {
    vector<vector<int>> grid;
    ifstream file(filename);
    string line;
    while (getline(file, line)) {
        int space = line.find(' ');
        grid.push_back({stoi(line.substr(0, space)), stoi(line.substr(space + 1))});
    }
    return grid;
}


int main() {
    vector<vector<int>> grid = read_grid("grids/grid1.txt");
    for (int i = 0; i < grid.size(); i++) {
        cout << grid[i][0] << " " << grid[i][1] << endl;
    }
    return 0;
}