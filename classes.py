import numpy as np
import pandas as pd
import tests
from collections import namedtuple

TilePos = namedtuple("pos",["row", "col", "box"])
BoxRel = namedtuple("boxrel", ["hor", "ver"])
box_rel = {1: BoxRel([2,3], [4,7]), 2: BoxRel([1,3], [5,8]),        
                        3: BoxRel([1,2], [6,9]), 4: BoxRel([5,6], [1,7]),
                        5: BoxRel([4,6], [2,8]), 6: BoxRel([4,5], [3,9]),
                        7: BoxRel([8,9], [1,4]), 8: BoxRel([7,9], [2,5]),
                        9: BoxRel([7,8], [3,6])}      

class Tile:

    def __init__(self, row: int, col: int, init_value = None):
        self.num = (row - 1) * 9 + col
        self.tilePos = TilePos(row, col, 3*((row-1)//3) + (col - 1)//3 + 1)

        self.value = init_value
        if self.value:
            self.poss_nums = []
            self.is_empty = False
            self.display = self.value
        else:
            self.poss_nums = list(range(1,10))
            self.is_empty = True
            self.display = ' '

    def __repr__(self):
        return "t"+str(self.num)

    def update(self):
        """
        Checks whether there is only a single possibility for the present tile and inserts it in this case (and removes it from the poss_nums list). Furthermore, returns True if the tile was filled and False if not.
        """
        if len(self.poss_nums) == 1:
            self.value = self.poss_nums.pop()
            self.is_empty = False
            self.display = self.value
            return self
        else:
            return False

    def find_neighbors(self, sudoku):
        """
        Returns a list of all tile objects in sudoku that influence the present tile.
        """
        r, c, b = self.tilePos
        neighbors = []
        for tile in sudoku.tiles.values():
            if tile.tilePos.row == r or tile.tilePos.col == c or tile.tilePos.box == b:
                neighbors.append(tile)
        neighbors.remove(self)

        return neighbors
    
    def check_r_c_b(self, sudoku):
        """
        Collects all influencing tiles and removes their values from the present poss_nums list. Then, the present tile is updated and the output from .update() is returned.
        """
        neighbors = self.find_neighbors(sudoku)

        for tile in neighbors:
            if tile.value in self.poss_nums:
                self.poss_nums.remove(tile.value)
        return self.update()
    
    def insert(self, value):
        """
        Manually insert a value into a tile and update it.
        """
        self.poss_nums = [value]
        return self.update()
    
class Sudoku:

    def __init__(self, csv_file):
        """
        Load and check the Sudoku given in the csv-file and create the 81 tiles. Then, further create for every box, row and column a list containing all the numbers that are already present. These lists 
        are put into a dictionary, one for boxes, one for rows and one for columns. Lastly, we check whether the Sudoku is correct so far. 
        """
        self.file = pd.read_csv(csv_file, delimiter=",", header = None)
        self.check_csv()
        self.init_tiles()

        self.boxes, self.rows, self.cols = {}, {}, {}
        for i in range(1,10):
            self.boxes[i] = {tile.value for tile in self.tiles.values() if (tile.tilePos.box == i and tile.value)}
            self.rows[i] = {tile.value for tile in self.tiles.values() if (tile.tilePos.row == i and tile.value)}
            self.cols[i] = {tile.value for tile in self.tiles.values() if (tile.tilePos.col == i and tile.value)}
        
        self.num_lists = [self.rows, self.cols, self.boxes]
        self.check_sudoku()

    def init_tiles(self):
        """
        We create a dictionary of 81 tiles and we save the initial Sudoku configuration. Then, we also initialize the list of yet empty tiles.
        """
        self.tiles = {}
        self.filled_tiles = 0
        for r in range(1,10):
            for c in range(1,10):
                if self.file[c-1][r-1] in ['', ' ', '  ']:
                    tile = Tile(r,c)
                else:
                    tile = Tile(r,c, int(self.file[c-1][r-1]))
                    self.filled_tiles += 1

                self.tiles[str(tile)] = tile

        self.initial_state = self.display(show=False)
        self.empty_tiles = [tile for tile in self.tiles.values() if tile.is_empty]

    def update_sudoku_attributes(self, tile):
        """
        For a given tile that was just filled, update the Sudoku attributes.
        """
        r,c,b = tile.tilePos
        if tile in self.empty_tiles:
            self.empty_tiles.remove(tile)
        self.boxes[b].add(tile.value)
        self.rows[r].add(tile.value)
        self.cols[c].add(tile.value)
        self.filled_tiles = 81 - len(self.empty_tiles)

    def give_possibilites(self, num: int, index: int, structure: int):
        poss_tiles = [tile for tile in self.empty_tiles if tile.tilePos[structure] == index and num in tile.poss_nums] 
        return poss_tiles
    
    def check_csv(self):
        """
        Checks if only input in [1,2,3,4,5,6,7,8,9,, ,  ] is given.
        """
        for c in range(1,10):
            for r in range(1,10):
                if self.file[c-1][r-1] not in [str(k) for k in range(1,10)]+['', ' ', '  ']:
                    raise Exception(tests.CsvError,"Check that the input consists of integers or whitespaces!")

    def check_sudoku(self):
        """
        Checks for the correctness of the sudoku according to the rules of sudoku
        """
        for i in range(1,10):
            if len(self.boxes[i]) != len(set(self.boxes[i])):
                raise Exception(tests.BoxError,"Box {} is wrong".format(i))
            
            if len(self.cols[i]) != len(set(self.cols[i])):
                raise Exception(tests.BoxError,"Column {} is wrong".format(i))
            
            if len(self.rows[i]) != len(set(self.rows[i])):
                raise Exception(tests.BoxError,"Row {} is wrong".format(i))
            
    def display(self, show = True, input_grid = None):
        """
        A function to present the state of the Sudoku in a readable format. Can also be used to print a given input state.
        """
        number_line = 2*'| {} ¦ {} ¦ {} |' + '| {} ¦ {} ¦ {} |\n'
        fat_rule = 2*' ___ ___ ___ ' + ' ___ ___ ___ \n'
        rule = 2*' --- --- --- ' + ' --- --- --- \n'
        
        self.value_list = [self.tiles['t'+str(index)].display for index in range(1,82)]        
        self.grid = (3*(fat_rule + "\n" + 2*(number_line + rule) + number_line + fat_rule)).format(*self.value_list)

        if input_grid:
            grid = input_grid
            show = True
        else:
            grid = self.grid
        
        if show:
                print(grid)
        return grid