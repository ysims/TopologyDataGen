from abc import ABC, abstractmethod
import copy
import itertools
import math
from operator import add
import random


class RandomWalk(ABC):

    # Creates a random walk and adds it to the grid
    # The walk starts in some defined location and
    # randomly moves in any direction, with no
    # intersections or touching of other objects
    # or itself (preventing loops in the walk)
    # If it fails to work, it returns False,
    # True otherwise
    def _random_walk(self):
        # Keep track of all the points in the tunnel
        all_points = self._get_start()
        if not all_points:
            return False

        self.isBranching = False
        original_grid = copy.copy(self.grid)
        if not self._walk(all_points):
            self.grid = original_grid
            return False

        # The last two points won't be there,
        # add everything in the walk to the grid
        for points in all_points:
            for point in points:
                indexing = ""
                for i in range(self.dimensions):
                    indexing += "[" + str(point[i]) + "]"
                exec("self.grid" + indexing + " = True")
                # self.grid[point[0]][point[1]][point[2]] = True

        # Nothing seemed to go wrong and we
        # don't want to branch so return true
        if not self.branching:
            return True
        # Flag to allow for different functionality in functions when branching
        self.isBranching = True
        # Loop until there are no more paths to
        # check for branching
        paths = []
        paths.append(copy.copy(all_points))
        while paths:
            # Find out how many branches should be made
            num_branch = self._num_branches(paths[0])
            if num_branch == 0:
                paths.remove(paths[0])
                continue
            # Loop while we have branches to create
            max_tries = 10000
            amount_tried = 0
            while num_branch > 0 and amount_tried < max_tries:
                amount_tried += 1
                # Get the start of our branch
                # If we can't make any branch on this
                # path, stop trying with this path
                all_points = self._branch_start(paths[0])
                # No need to remove the path because
                # we do it after breaking
                if not all_points:
                    break

                # Do as before and create the path
                # If it doesn't work, try again
                original_grid = copy.copy(self.grid)
                if not self._walk(all_points):
                    self.grid = original_grid
                    continue

                # The last two points won't be there,
                # add everything in the walk to the grid
                for points in all_points:
                    for point in points:
                        indexing = ""
                        for i in range(self.dimensions):
                            indexing += "[" + str(point[i]) + "]"
                        exec("self.grid" + indexing + " = True")
    
                # Successfully made a branch
                num_branch -= 1
                amount_tried = 0
                paths.append(copy.copy(all_points))

            # Finished adding all the branches to this path
            paths.remove(paths[0])

        return True

    def _walk(self, all_points):
        # Add all possible movement directions
        movement_direction = []  # list of value movements
        for perm in itertools.permutations([1, 0, 0], self.dimensions):
            movement_direction.append(list(perm))
            movement_direction.append([-x for x in list(perm)])
        movement_direction.sort()
        # Remove duplicates
        movement_direction = list(
            movement_direction
            for movement_direction, _ in itertools.groupby(movement_direction)
        )
        # Loop until some given condition is satisfied
        # Shuffle so we don't always go the same way
        # Check if the point works
        # If it does, add it to the walk
        # If it doesn't, try again
        # If we can't add any points, see if it's ok
        # If it worked or we're happy with the attempt, return true
        # If it didn't work then return false
        # The walk list contains the last two points but the grid does not,
        # Otherwise they would be flagged as intersections
        while not self._stop_walk_condition(all_points):
            point_added = False
            random.shuffle(movement_direction)
            for direction in movement_direction:
                # Add the direction and the last point
                if self._try_add(direction, all_points):
                    point_added = True
                    break  # Don't keep going with the for loop

            # If a point wasn't added
            # see if this was a decent enough try
            # otherwise just return false
            if not point_added:
                if not self._acceptable_walk(all_points):
                    # Remove anything we added because we don't want it anymore
                    for points in all_points:
                        for point in points:
                            indexing = ""
                            for i in range(self.dimensions):
                                indexing += "[" + str(point[i]) + "]"
                            exec("self.grid" + indexing + " = False")
                    return False
                else:
                    return True
        return True

    # Try to add a point to the tunnel
    def _try_add(self, direction, all_points):
        # ***** Get the next point in the spine and check it *****
        # The next point in the spine of the tunnel
        # Check it doesn't touch the grid and
        # don't repeat a point we've already done
        next_point = list(map(add, direction, all_points[len(all_points) - 1][0]))
        if self._grid_check(next_point):
            return False
        for points in all_points:
            if next_point == points[0]:
                return False

        # ***** Determine width *****
        if len(all_points[len(all_points) - 1]) > 1:
            previous_width = int(math.log(len(all_points[len(all_points) - 1]), 2))
        else:
            previous_width = 1

        width = min(
            max(
                random.randrange(previous_width - 1, previous_width + 2), self.min_width
            ),
            self.max_width,
        )

        # ***** Sort out the grid *****
        my_grid = copy.copy(self.grid)

        if len(all_points) > 2 + width:
            for index, points in enumerate(all_points):
                for point in points:
                    if (len(all_points) - width) > index:
                        indexing = ""
                        for i in range(self.dimensions):
                            indexing += "[" + str(point[i]) + "]"
                        exec("self.grid" + indexing + " = True")
                    else:
                        indexing = ""
                        for i in range(self.dimensions):
                            indexing += "[" + str(point[i]) + "]"
                        exec("self.grid" + indexing + " = False")
    
        # ***** Add it to the list and try to add the border *****
        points_to_be_added = [next_point]
        if not self._add_point_and_border(points_to_be_added, direction, width):
            return False

        # It worked! Add this next set of points to the path
        all_points.append(points_to_be_added)
        self.grid = my_grid
        return True

    def _add_point_and_border(self, points_to_be_added, direction, width):
        # Points to add a border to, starting with the spine
        recurse_border = [points_to_be_added[0]]

        for _ in range(0, width - 1):
            new_recurse_border = []  # the next set of points to add the border to
            border = [[0, 1], [1, 0], [1, 1]]
            add_border = (
                [[0, b[0], b[1]] for b in border]
                if direction[0] != 0
                else [[b[0], 0, b[1]] for b in border]
                if direction[1] != 0
                else [[b[0], b[1], 0] for b in border]
            )
            # Add the border points to expand the width
            for recurse_border_point in recurse_border:
                for border in add_border:
                    try:  # skip if this is out of bounds
                        # Point to try to add
                        test_point = []
                        for i in range(self.dimensions):
                            test_point.append(recurse_border_point[i] + border[i])
                        # Don't want to intersect/touch the grid
                        if not self._grid_check(test_point):
                            # Don't add it if it's already there
                            if points_to_be_added.count(test_point) == 0:
                                points_to_be_added.append(test_point)
                                new_recurse_border.append(test_point)
                        else:
                            return False
                    except:
                        pass
        return True

    # Determines a start location for the walk
    # and returns the first point in the walk
    @abstractmethod
    def _get_start(self):
        pass

    # Checks if the point touches the grid
    # Returns True if the point touches or intersects the grid
    # Returns False otherwise
    @abstractmethod
    def _grid_check(self, point):
        print("second hello")
        pass

    # Returns True if the walk should stop
    # False otherwise
    @abstractmethod
    def _stop_walk_condition(self, all_points):
        pass

    # In case the walk doesn't stop normally
    # with the _stop_walk_condition()
    # this determines if the walk is acceptable to use
    # Returns True if it can be used
    # False otherwise
    @abstractmethod
    def _acceptable_walk(self, all_points):
        pass

    # Given the path, how many times will we branch from it?
    def _num_branches(self, path):
        # -2 from endpoints (no branches on endpoints)
        if len(path) < self.length_between_branches - 2:
            return 0
        return math.floor(len(path) / self.length_between_branches)

    # Find a point to branch from on the path
    # and return the beginning of the new path
    def _branch_start(self, _path):
        # This tentacle will be smaller than its parent
        if int(len(_path) / 2) <= int(self.min_branch_length / 2):
            return []
        self.branch_length = random.randrange(
            int(self.min_branch_length / 2), int(len(_path) / 2), 1
        )

        path = copy.copy(_path)

        # This is the path we choose a point from
        # It has the first and last taken out
        choice_path = copy.copy(_path)
        choice_path.pop(0)
        choice_path.pop(len(choice_path) - 1)

        new_path = []
        max_tries = 1000
        amount_tried = 0
        while (not new_path) and (amount_tried < max_tries):
            amount_tried += 1

            path = copy.copy(_path)
            start = random.choice(choice_path)

            # Remove this point and adjacent points so we can
            # do intersect or touch properly
            index = path.index(start)
            before = path.pop(index - 1)

            # Get the direction that the parent branch is moving in
            # and chose a random direction that is not the direction of the parent
            # to move in, so that the branch moves away from the parent
            start_point = start[0]
            before_point = before[0]
            direction = []
            for i in range(self.dimensions):
                direction.append(start_point[i] - before_point[i])

            directions = (
                [[0, 1, 0], [0, 0, 1], [0, -1, 0], [0, 0, -1]]
                if direction[0] == 0
                else [
                    [1, 0, 0],
                    [0, 0, 1],
                    [-1, 0, 0],
                    [0, 0, -1],
                ]
                if direction[1] == 0
                else [
                    [1, 0, 0],
                    [0, 1, 0],
                    [-1, 0, 0],
                    [0, -1, 0],
                ]
            )
            random.shuffle(directions)

            # Remove these points from the grid so that intersection/touch checking
            # doesn't stop the walk from moving
            for i in range(index - 2, index + 2):
                for point in _path[i]:
                    indexing = ""
                    for i in range(self.dimensions):
                        indexing += "[" + str(point[i]) + "]"
                    exec("self.grid" + indexing + " = False")

            for direction in directions:
                new_start = []
                for i in range(self.dimensions):
                    new_start.append(start_point[i] + direction[i])
                # Add in this point with its border, with minimum width
                new_points = [new_start]
                if not self._add_point_and_border(
                    new_points, direction, self.min_width
                ):
                    continue

                new_path = [new_points]

            # Add the parent path points back in
            for i in range(index - 2, index + 2):
                for point in _path[i]:
                    indexing = ""
                    for i in range(self.dimensions):
                        indexing += "[" + str(point[i]) + "]"
                    exec("self.grid" + indexing + " = True")

        return new_path
