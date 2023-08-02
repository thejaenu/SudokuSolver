from classes import *
from itertools import combinations

def unique(lst):
    unique_list = [element for n, element in enumerate(lst) if element not in lst[:n]]
    return unique_list
class Solver(Sudoku):

    def __init__(self, csv_file):
        Sudoku.__init__(self, csv_file)
        self.func_repeater(self.cycle)

    def check_neighbors(self):
        """
        Iterates through the empty tiles and considers all related tiles to check whether there is only a single possibility left. Also proceeds in doing a cascade check and updating the Sudoku attributes.
        """
        updated_list = []
        for tile in self.empty_tiles:
            was_updated = tile.check_r_c_b(self)
            if was_updated:
                updated_list.append(tile)
        for updated_tile in updated_list:
            self.cascade_check(updated_tile)
            self.update_sudoku_attributes(updated_tile)
        

    def check_number(self, number: int, structure: int):
        """
        For a given number and structure (row, column or box, encoded as 0,1 and 2), checks for every such structure element (i.e. every row, column or box) whether there is only a single possibility left for this number.
        """
        if structure not in [0,1,2]:
            print("Parameter structure must be 0 (row), 1 (column) or 2 (box)!")
            return
        for i in range(1,10):
            poss_in_i = [tile for tile in self.empty_tiles if ((tile.tilePos[structure] == i) and (number in tile.poss_nums) and (number not in self.num_lists[structure][i]))]
            if len(poss_in_i) == 1:
                tile = poss_in_i[0]
                tile.insert(number)
                self.cascade_check(tile)
                self.update_sudoku_attributes(tile)

    def check_structure(self, structure: int):
        """
        Very similar to check_number, but starts with a structure (row, column or box), iterates over its entities, and always considers whether there is only a single possibility left for all missing numbers in this entity.
        """
        if structure not in [0,1,2]:
            print("Parameter structure must be 0 (row), 1 (column) or 2 (box)!")
            return
        num_dict = self.num_lists[structure]
        for i in range(1,10):
            empty_tiles_in_struct = [tile for tile in self.empty_tiles if tile.tilePos[structure] == i]
            missing_nums = [num for num in range(1,10) if num not in num_dict[i]]
            for num in missing_nums:
                poss_tiles = [tile for tile in empty_tiles_in_struct if num in tile.poss_nums]
                if len(poss_tiles) == 1:
                    tile = poss_tiles[0]
                    tile.insert(num)
                    self.cascade_check(tile)
                    self.update_sudoku_attributes(tile)

    def row_or_col_restriction(self, box_index: int):
        """
        Takes a box_index as input, and then finds out whether in this box, a missing number can be restricted to a single row. If so, the tiles in this box and row contain the number for sure, so we can remove the number from pos_num in the neighboring boxes in this particular row. Ex.: If we know that in box 1, the number 5 can only be in the first row, we know that in box 2 and 3, the number 5 cannot be in row 1 etc.
        """
        missing_nums = [num for num in range(1,10) if num not in self.boxes[box_index]]
        for structure in [0,1]:
            neighbor_boxes = box_rel[box_index][structure]
            empty_tiles = [tile for tile in self.empty_tiles if tile.tilePos.box == box_index]
            for num in missing_nums:
                poss_r_c = [tile.tilePos[structure] for tile in empty_tiles if num in tile.poss_nums]
                if len(set(poss_r_c)) == 1:
                    for tile in self.empty_tiles:
                        if tile.tilePos.box in neighbor_boxes and tile.tilePos[structure] == poss_r_c[0]:
                            if num in tile.poss_nums:
                                tile.poss_nums.remove(num)
                            was_updated = tile.update()
                            if was_updated:
                                self.update_sudoku_attributes(tile)

    def check_for_pairs_or_triplets(self, size):
        for structure in range(3):
            for i in range(1,10):
                poss_nums = [num for num in range(1,10) if num not in self.num_lists[structure][i]]
                if len(poss_nums) >= size:
                    for comb in combinations(poss_nums, size):
                        list_poss_tiles = [self.give_possibilites(num, i, structure) for num in comb]
                        if len(unique(list_poss_tiles)) == 1 and len(list_poss_tiles[0]) == size:
                            print(structure, i)
                            print(comb)
                            print(list_poss_tiles)
                            combined_tiles = self.give_possibilites(comb[0], i, structure)
                            eliminated_nums = set()
                            for tile in combined_tiles:
                                for num in tile.poss_nums: 
                                    if num not in comb:
                                        eliminated_nums.add(num)

                            for tile in combined_tiles:
                                tile.poss_nums = list(comb)
    
    def cycle(self):
        self.check_neighbors()
        for i in range(1,10):
            for j in range(2):
                self.func_repeater(self.check_number,i,j)
                self.row_or_col_restriction(i)
                self.check_structure(j)
        for size in [2,3]:
            self.check_for_pairs_or_triplets(size)
        self.check_sudoku()

    def func_repeater(self, func, *args):
        """
        Applies a given function repeatedly if it leads to progress in solving the Sudoku
        """
        current_grid = self.display(show=False)
        func(*args)
        new_grid = self.display(show=False)
        if current_grid != new_grid:
            self.func_repeater(func, *args)
        else:
            return
        
    def cascade_check(self, tile):
        """
        Intended for freshly filled tiles. Checks whether the related tiles can now also be updated. If a related tile can be filled, the function is also applied to this tile.
        """
        neighbors = tile.find_neighbors(self)

        for neighbor in neighbors:
            was_updated = neighbor.check_r_c_b(self)
            if was_updated:
                self.update_sudoku_attributes(neighbor)
                self.cascade_check(neighbor)
        
s = Solver("20min_schwer.csv")
s.display()