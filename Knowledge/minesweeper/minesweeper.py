import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        self.combinations = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def neighbours(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        height = 8
        width = 8
        neighbours = list()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < height and 0 <= j < width:
                    neighbours.append((i, j))
        return neighbours

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        # returns all neighbour cells for that safe cell with the number and creates a sentence with it
        S1 = Sentence(self.neighbours(cell), count)
        for mine in self.mines:
            if mine in S1.cells:
                S1.mark_mine(mine)
        for safe in self.safes:
            if safe in S1.cells:
                S1.mark_safe(safe)
        # we need to do a self upgrade to the sentece to remove mines or safes if the sentence suggest that all adjacent are mines or safes
        # This doesn't remove the previously known mines
        # The next line ensures that if S1 contains all mines or all safes just add them to self.mines and self.safes and don't make a sentence with them
        if S1.known_mines():
            x = copy.deepcopy(S1.known_mines())
            for cell in x:
                self.mark_mine(cell)
        elif S1.known_safes():
            x = copy.deepcopy(S1.known_safes())
            for cell in x:
                self.mark_safe(cell)
        # This else adds a sentence to the knowledge base, now that we know that the sentence doesn't ALL have mines or safes
        # HOWEVER, in the future if we discovered new mines or safes, this sentence will be updated as by line 219 an line 222 which includes
        # looping throught each sentence, now that our sentence is an old sentence in the knowledge list, and extract the mine from that sentence and update it
        else:
            self.knowledge.append(S1)
        # Now that we finished either making a new sentence in self.knowledge or extracting all safes because count of the cell added to knowledge was 0, so we took all the neighbours to be safe in self.safes and we didn't add that sentences
        # Along that, if we identified all mines or all safes around a given cell , we update all existing knoweldge base so if we had {G, E, F} = 2 in a knowledge base and we updated this by the above functions because for instance we identified from a recent knowledge that F is a safe
        # Then the updated sentence in this knowledge due to above functions is now {G, E} = 2, we can extract more information after this updated information, because we know that if {G, E} = 2 then {G, E} are both mines , so we loop again now over the sentences to extract further info from the old knowledge
        while not all(sentence.known_safes() == None and sentence.known_mines() == None for sentence in self.knowledge):
            for sentence in reversed(self.knowledge):
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                    continue
                if sentence.known_mines():
                    # Here we are making a deepcopy of sentence.known_mines because when self.mark_mine(cell) is executed, sentence.known_mines changes for exmple from {G, E} = 2 to {G} = 1 , so the iterable gives an error
                    x = copy.deepcopy(sentence.known_mines())
                    for cell in x:
                        self.mark_mine(cell)
                        # removing the sentence from the knowledge bec all the cells in this sentence are identified as mines or safes and all the cells are wiped out from its original sentence
                        # So if in this case all cells are mine cells, then on each self.mark_mine(cell), the mine cell is extracted from the sentences and finally after the loop, the sentence that had for instance {G, E} = 2 would be {} = 0
                        # It's obvious now why we'll want to remove that rubbish sentence from the knowledge
                    self.knowledge.remove(sentence)
                elif sentence.known_safes():
                    x = copy.deepcopy(sentence.known_safes())
                    for cell in x:
                        self.mark_safe(cell)
                    self.knowledge.remove(sentence)
        # Now the knowledge contains only sentences where neither we know that all of the cells are mines or all of them are safes
        # The following line takes combinations of sentences for ex if there are {S1, S2, S3, S4} in self.knowledge, then a new list is generated with a tuple combination of [(S1,S2), (S1,S3), (S1,S4), (S2,S3), (S2,S4), (S3,S4)], SO  a combination of each sentence with another sentence is formed to check if a sentence is a subset of another sentence in order to make a new knowledge based on that.
        # From a sentence we have {A, B, C} = 1. From the other sentence in the knowledge, we have {A, B, C, D, E} = 2. Logically, we could then infer a new piece of knowledge, that {D, E} = 1. After all, if two of A, B, C, D, and E are mines, and only one of A, B, and C are mines, then it stands to reason that exactly one of D and E must be the other mine.
        # This deep copy is a screenshot of what's inside self.knowledge, bec if removed sth or added sth in self.knowledge, second iteration in self.knowledge would be altered by the new updated self.knowledge
        p = copy.deepcopy(self.knowledge)
        for sentence, other_sentence in list(itertools.combinations(p, 2)):
            # If the two sentences are identical in knowledge, then delete one and leave the other and DON'T make another new sentence
            # It's an EXTRA check, I guess it won't harm if removed
            if len(sentence.cells) == 0 or len(other_sentence.cells) == 0:
                continue
            if sentence.cells == other_sentence.cells and sentence.count == other_sentence.count:
                continue
            if (sentence, other_sentence) in self.combinations or (other_sentence, sentence) in self.combinations:
                continue
            if sentence.cells.issubset(other_sentence.cells):
                new_sent_cells = other_sentence.cells - sentence.cells
                new_sent_count = other_sentence.count - sentence.count
                # This list is for collecting the 2 subset sentences in order to get rid of them at the end and leavae the new baby sentence
                if (sentence, other_sentence) not in self.combinations:
                    self.combinations.append((sentence, other_sentence))
                # Checking the newly added sentence if all of it has mines or safes
                S = Sentence(new_sent_cells, new_sent_count)
                for mine in self.mines:
                    if mine in S.cells:
                        S.mark_mine(mine)
                for safe in self.safes:
                    if safe in S.cells:
                        S.mark_safe(safe)

                if S.known_mines():
                    x = copy.deepcopy(S.known_mines())
                    for cell in x:
                        self.mark_mine(cell)
                elif S.known_safes():
                    x = copy.deepcopy(S.known_safes())
                    for cell in x:
                        self.mark_safe(cell)
                else:
                    self.knowledge.append(S)

            elif other_sentence.cells.issubset(sentence.cells):
                new_sent_cells = sentence.cells - other_sentence.cells
                new_sent_count = sentence.count - other_sentence.count
                if (other_sentence, sentence) not in self.combinations:
                    self.combinations.append((other_sentence, sentence))
                S = Sentence(new_sent_cells, new_sent_count)
                for mine in self.mines:
                    if mine in S.cells:
                        S.mark_mine(mine)
                for safe in self.safes:
                    if safe in S.cells:
                        S.mark_safe(safe)

                if S.known_mines():
                    x = copy.deepcopy(S.known_mines())
                    for cell in x:
                        self.mark_mine(cell)
                elif S.known_safes():
                    x = copy.deepcopy(S.known_safes())
                    for cell in x:
                        self.mark_safe(cell)
                else:
                    self.knowledge.append(S)
            # In this for loop we didn't take a deepcopy of self.knowledge, bec if a sent had all mines or safes, then it will update the knowledge and the other loop becomes an upated sentence, if any. Reversed list as when we remove an item, the index pattern in the for loop doesn't skip iter
        while not all(sentence.known_safes() == None and sentence.known_mines() == None for sentence in self.knowledge):
            for sentence in reversed(self.knowledge):
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                    continue
                if sentence.known_mines():
                    x = copy.deepcopy(sentence.known_mines())
                    for cell in x:
                        self.mark_mine(cell)
                    self.knowledge.remove(sentence)
                elif sentence.known_safes():
                    x = copy.deepcopy(sentence.known_safes())
                    for cell in x:
                        self.mark_safe(cell)
                    self.knowledge.remove(sentence)
        print('=================================')
        print('Mine Field!')
        print(self.mines)
        print('=================================')

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Contains all safe moves saved (could be any safe move),However it must not be an already made move
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        random_m = []
        # This happens only at the first move
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    random_m.append((i, j))
        if len(random_m) != 0:
            return random.choice(random_m)
        return None
