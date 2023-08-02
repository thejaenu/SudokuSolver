import csv
import pandas as pd
import tests

class Tile:

    def __init__(self, row: int, col: int, init_value = None):
        self.row = row
        self.col = col
        self.num = (self.row - 1) * 9 + self.col
        self.box = 3*((self.row-1)//3) + (self.col - 1)//3 + 1

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
            return True
        else:
            return False

    def find_neighbors(self, sudoku):
        """
        Returns a list of all tile objects in sudoku that influence the present tile.
        """
        r, c, b = self.row, self.col, self.box
        neighbors = []
        for tile in sudoku.tiles.values():
            if tile.row == r or tile.col == c or tile.box == b:
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
    
    def _insert(self,value):
        self.poss_nums = [value]
        self.update()
    
class Sudoku:

    def __init__(self, csv_file):
        self.file = pd.read_csv(csv_file, delimiter=",", header = None)
        self.check_csv()
        self.init_tiles()
        self.check_sudoku()

        self.boxes, self.rows, self.cols = {}, {}, {}
        for i in range(1,10):
            self.boxes[i] = sorted([tile.value for tile in self.tiles.values() if (tile.box == i and tile.value)])
            self.rows[i] = sorted([tile.value for tile in self.tiles.values() if (tile.row == i and tile.value)])
            self.cols[i] = sorted([tile.value for tile in self.tiles.values() if (tile.col == i and tile.value)])
        
    def init_tiles(self):
        self.tiles = {}
        for r in range(1,10):
            for c in range(1,10):
                if self.file[c-1][r-1] in ['', ' ', '  ']:
                    tile = Tile(r,c)
                else:
                    tile = Tile(r,c, int(self.file[c-1][r-1]))

                self.tiles[str(tile)] = tile

        self.initial_state = self.display(show=False)
        self.empty_tiles = [tile for tile in self.tiles.values() if tile.is_empty]

        for tile in self.empty_tiles:
            was_updated = tile.check_r_c_b(self)
            if was_updated:
                self.empty_tiles.remove(tile)

    def check_csv(self):
        for c in range(1,10):
            for r in range(1,10):
                if self.file[c-1][r-1] not in [str(k) for k in range(1,10)]+['', ' ', '  ']:
                    raise Exception(tests.CsvError,"Check that the input consists of integers or whitespaces!")

    def check_sudoku(self):
        '''Checks for the correctness of the sudoku according to the rules of sudoku'''
        for i in range(1,10):
            if len(self.boxes[i]) != len(set(self.boxes[i])):
                raise Exception(tests.BoxError,"Box {} is wrong".format(i))
            
            if len(self.cols[i]) != len(set(self.cols[i])):
                raise Exception(tests.BoxError,"Column {} is wrong".format(i))
            
            if len(self.rows[i]) != len(set(self.rows[i])):
                raise Exception(tests.BoxError,"Row {} is wrong".format(i))
            
    def display(self, show = True, input_grid = None):
        number_line = 2*'| {} ¦ {} ¦ {} |' + '| {} ¦ {} ¦ {} |\n'
        fat_rule = 2*' ___ ___ ___ ' + ' ___ ___ ___ \n'
        rule = 2*' --- --- --- ' + ' --- --- --- \n'
        
        self.value_list = [self.tiles['t'+str(index)].display for index in range(1,82)]        
        self.grid = (3*(fat_rule + 2*(number_line + rule) + number_line + fat_rule)).format(*self.value_list)

        if input_grid:
            grid = input_grid
            show = True
        else:
            grid = self.grid
        
        if show:
                print(grid)
        return grid

s = Sudoku("example.csv")


