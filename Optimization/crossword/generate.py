import sys
import copy
from crossword import *
from itertools import combinations


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            # Taking a copy of set bec we are deleting items along the way
            for word in copy.copy(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        i, j = self.crossword.overlaps[x, y]
        conflict_count = 0
        revised = False
        # For every word in X check if there is a possible value in Y to not violate the constraint
        for word in copy.copy(self.domains[x]):
            for w in self.domains[y]:
                if word[i] != w[j]:
                    conflict_count += 1
            # If conflict_count == len(self.domains[y]) then for this value of X, it doesn't have a value in Y to not violate the constraints between both variables
            if conflict_count == len(self.domains[y]):
                # We'll remove a value from X's domain so revised = true
                revised = True
                self.domains[x].remove(word)
            conflict_count = 0
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # First time for checking ar consistency within the whole domain
        if arcs is None:
            queue = [(x, y) for x, y in self.crossword.overlaps if self.crossword.overlaps[x, y] != None]
        # The queue will take specific arcs if it was called from backtrack
        else: queue = arcs
        while len(queue) != 0:
            # Removing one element from the queue (2 variables  to check if they are arc consistent)
            X, Y = queue.pop()
            if self.revise(X, Y):
                if len(self.domains[X]) == 0:
                    return False
                # If self.revise(X, Y) is true then X's domain has been manipulated so we need to add its neighbors and this variable to the queue to check their consistency again
                for el in self.crossword.neighbors(X) - {Y}:
                    queue.append((el, X))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return True if len(assignment) == len(self.crossword.variables) else False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check that the words in the assignment are unique
        if any([x == y for x, y in list(combinations(assignment.values(), 2))]):
            return False
        for var in assignment:
            # Check for length of each value of each variable
            if len(assignment[var]) != var.length:
                return False
            for neighbor in [neighbor for neighbor in self.crossword.neighbors(var) if neighbor in assignment]:
                # Check for binary constraints within variables in the assignment
                i, j = self.crossword.overlaps[var, neighbor]
                if assignment[var][i] != assignment[neighbor][j]:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Function called by the sort KEY to be applied to each element.
        def Count(el):
            count = 0
            for v in set(self.domains) - {var} - set(assignment):
                if v not in self.crossword.neighbors(var):
                    continue
                if el in self.domains[v]:
                    count += 1
            return count
        # Making a list of domain values for that variable (which is already in self.domain)
        lst = list(self.domains[var])
        # Sorting the list based on the given heuristic
        # Count function is called on each element in the list and a number is produced (number of presence in the Overlapping neighbours domain)
        # The list is then sorted in ascending order based on that number
        lst.sort(key=Count)
        return lst

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        def num_values(el):
            return len(self.domains[el])
        # Returning a list of unassigned vars and then sorting them according to number of elements

        def num_neighbors(el):
            return len(self.crossword.neighbors(el))
        remaining_vars = list(set(self.domains) - set(assignment))
        remaining_vars.sort(key=num_values)
        lst = []
        lst.append(remaining_vars[0])
        # min_length is minimum length of elements, since it's sorted ascendingly so the least number of elements is in the first variable in the lista
        min_length = len(self.domains[remaining_vars[0]])
        # Looping again on the list to check if more than one element has the same minimum number in order to implement the second heuristic
        for i in range(len(remaining_vars)):
            if i != 0 and len(self.domains[remaining_vars[i]]) == min_length:
                # Appending in lst only if a variable has the same number of elements as the first variable(which has the least number of values)
                lst.append(remaining_vars[i])
        # If the length is one then there was no other variable having minimum number of elements as the first variable except the first variable with min length
        if len(lst) == 1:
            return remaining_vars[0]
        # This code is executed only if there was 1 or more variable having same minimum length of values
        lst.sort(key=num_neighbors, reverse=True)
        return lst[0]

    def INFERENCE(self, var, assignment):
        d = dict()
        for el in assignment:
            self.domains[el] = {assignment[el]}
        # self.domains isn't updated with the values of variables present in the assignment, so this loop updates self.domains with the only value present for that variable
        if self.ac3([(Y, var) for Y in self.crossword.neighbors(var) if Y not in assignment]):
            for x in [v for v in self.domains if len(self.domains[v]) == 1 and v not in assignment]:
                d[x] = list(self.domains[x])[0]
            return d
        # This code will execute if self.ac3 returned False : no possible solution for that variable
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete (terminator of the recursion)
        if self.assignment_complete(assignment):
            return assignment
        # Assign an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # Loop on the values of  the variable and each time assign it to that variable and check constraints
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            # If it passed the constraints test
            if self.consistent(assignment):
                # Inference function damages self.domains permenantly so a copy is provided in case inference was called and none returned (self.domain is still damaged because we tried predicting the future inferences but along the way we maniplulated self.domains)
                domain_copy = copy.copy(self.domains)
                inferences = self.INFERENCE(var, assignment)
                if inferences == None:
                    self.domains = domain_copy
                    del assignment[var]
                    continue
                if inferences != None:
                    # Inferences made are added to the assignment here
                    for v, val in inferences.items():
                        assignment[v] = val
                    # Backtrack is called again with the new assignment passed and then another variable is chosen and try to assign a value to it and check again whether the value violates constraints
                    result = self.backtrack(assignment)
                # When backtrack is called for the last time, assignment is returned (check first line), then the result of last backtrack = assignment, then if result!= None which is true, then return result to the last backtrack called, and this continues as if the last assignment is being passed from the newest backtrack function to the oldest backtrack function called returning the very last assignment
                if result != None:
                    return result
                # I already damaged self.domains when calling inference, but it wasn't fixed bec inference was != None ,However if backtracked to this variable again due to failure of future variables, we need to retrieve the old self.domains
                self.domains = domain_copy
            # If value wasn't consistent with the assignment, then this assignment[variable] is deleted and another value is chosen from the loop
            del assignment[var]
        # If for a given variable, all values were looped on and all of them violates the constraints, so there is no solution for that variable, then none is returned to the last backtrack it was called from and result != None passes and the assigned value for the variable before it is then deleted and looped on for another value, so the assignment is backtracked from a variable before.
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
