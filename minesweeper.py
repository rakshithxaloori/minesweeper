import itertools
import random


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
        # Return all cells if all cells are mines
        if (len(self.cells) == self.count) and (self.count > 0):
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Return all cells if no mines are in them
        if (self.count == 0) and len(self.cells) > 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # Delete the cell from self.cells
            # Decrease the self.count
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # Delete the cell from self.cells, the count remains same
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

        # Add left, right, up, down and diagonal cells as a sentence to the knowledge
        neighbourCells = set()
        i = cell[0]
        j = cell[1]
        p = i-1

        # Collect all the neighbours
        while p < i+2:
            q = j-1
            while q < j+2:
                if p > -1 and p < self.height and q > -1 and q < self.width:
                    if (p, q) not in self.moves_made:
                        neighbourCells.add((p, q))
                q += 1
            p += 1

        # Add only if the cell has any neighbour cells that haven't been explored yet
        if len(neighbourCells) > 0:
            newSentence = Sentence(cells=neighbourCells, count=count)
            self.knowledge.append(newSentence)

        # Check for subsets, if found add diff(super, subset) to the knowledge
        totalKnowledge = self.knowledge
        totalLength = len(totalKnowledge)
        newKnowledge = []
        for i in range(totalLength):
            for j in range(i+1, totalLength):
                # Check if there are any subsets to infer
                if totalKnowledge[i] != totalKnowledge[j] and (totalKnowledge[i].cells).issubset(totalKnowledge[j].cells):
                    diffSet = totalKnowledge[j].cells - \
                        totalKnowledge[i].cells
                    diffCount = totalKnowledge[j].count - \
                        totalKnowledge[i].count
                    newSentence = Sentence(cells=diffSet, count=diffCount)
                    if (newSentence not in newKnowledge) and (newSentence not in totalKnowledge):
                        newKnowledge.append(newSentence)

        # Only add to the knowledge if there's any new knowledge
        if len(newKnowledge) > 0:
            self.knowledge.extend(newKnowledge)

        # For all sentences check known_mines, known_safes
        knownMines = set()
        knownSafes = set()

        # Doing it this way avoids RuntimeError of the set changing it's size
        for sentence in self.knowledge:
            newKnownMines = sentence.known_mines()
            newKnownSafes = sentence.known_safes()
            if newKnownMines is not None:
                knownMines = knownMines | newKnownMines
            if newKnownSafes is not None:
                knownSafes = knownSafes | newKnownSafes

        if knownMines is not None:
            for knownMine in knownMines:
                self.mark_mine(knownMine)
        if knownSafes is not None:
            for knownSafe in knownSafes:
                self.mark_safe(knownSafe)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # All saves moves that are not have already been made
        safeNotMade = self.safes - self.moves_made

        # If no safe moves are available, return None
        if len(safeNotMade) == 0:
            return None

        # Return random safe move
        return random.sample(safeNotMade, 1)[0]

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        allMoves = set()
        for i in range(self.height):
            for j in range(self.width):
                allMoves.add((i, j))

        # Only moves available are that which have not been made yet and are not known mines
        movesAvailable = allMoves - self.moves_made - self.mines

        # No other moves are available
        if len(movesAvailable) == 0:
            return None

        # Return a random move from moves available
        return random.sample(movesAvailable, 1)[0]
