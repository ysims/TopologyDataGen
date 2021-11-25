from abc import ABC, abstractmethod
import copy
import itertools
import math
from operator import add
import random
import utils


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
        path = self._get_start()
        if not path:
            return False

        self.isBranching = False
        original_grid = copy.copy(self.grid)
        original_occupancy = copy.copy(self.occupancy_grid)
        original_tentacle_occupancy = copy.copy(self.tentacle_occupancy)
        if not self._walk(path):
            self.grid = original_grid
            self.occupancy_grid = original_occupancy
            self.tentacle_occupancy = original_tentacle_occupancy
            return False

        # The last points won't be there,
        # add everything in the walk to the grid
        # and update the occupancies
        for points in path:
            for point in points:
                utils.add_occupancy(self.occupancy_grid, point, self.object_min_distance)
                utils.add_occupancy(self.tentacle_occupancy, point, self.object_min_distance)
                self.grid[point[0]][point[1]][point[2]] = True

        # Nothing seemed to go wrong and there is no
        # branching so return true
        if not self.branching:
            return True
        # Flag to allow for different functionality in functions when branching
        self.isBranching = True
        # Loop until there are no more paths to
        # check for branching
        paths = [copy.copy(path)]
        while paths:
            # Find out how many branches should be made
            num_branch = self._num_branches(paths[0])
            if num_branch == 0:
                paths.remove(paths[0])
                continue
            # Loop while we have branches to create
            max_tries = 1000
            amount_tried = 0
            while num_branch > 0 and amount_tried < max_tries:
                amount_tried += 1
                # Get the start of our branch
                # If we can't make any branch on this
                # path, stop trying with this path
                path = self._branch_start(paths[0])
                # No need to remove the path because
                # we do it after breaking
                if not path:
                    break

                # Do as before and create the path
                # If it doesn't work, try again
                original_grid = copy.copy(self.grid)
                if not self._walk(path):
                    self.grid = original_grid
                    continue

                # The last two points won't be there,
                # add everything in the walk to the grid
                for points in path:
                    for point in points:
                        self.grid[point[0]][point[1]][point[2]] = True

                # Successfully made a branch
                num_branch -= 1
                amount_tried = 0
                paths.append(copy.copy(path))

            # Finished adding all the branches to this path
            paths.remove(paths[0])

        return True

    def _walk(self, path):
        # Add all possible movement directions
        movement_direction = []
        for x, y, z in itertools.permutations([1, 0, 0], 3):
            if movement_direction.count([x,y,z]) == 0:
                movement_direction.append([x, y, z])
            if movement_direction.count([-x,-y,-z]) == 0:
                movement_direction.append([-x, -y, -z])

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
        while not self._stop_walk_condition(path):
            point_added = False
            for direction in movement_direction:
                if self._try_add(direction, path):
                    point_added = True
                    break  # Don't keep going with the for loop
            # If a point wasn't added
            # see if this was a decent enough try
            # otherwise just return false
            if not point_added:
                if not self._acceptable_walk(path):
                    # Don't need to remove the points because the 
                    # original grid will be put back in upon returning
                    return False
                return True     # is an acceptable walk
        return True

    # Try to add a point to the tunnel
    def _try_add(self, direction, path):
        # ***** Get the next point in the spine and check it *****
        # The next point in the spine of the tunnel
        # Check it doesn't touch the grid and
        # don't repeat a point we've already done
        print(path)
        next_point = list(map(add, direction, path[len(path) - 1]))

        # ***** Determine width *****
        previous_width = utils.width(path[len(path) - 1])
        width = utils.clamp(
            random.randrange(previous_width - 1, previous_width + 2),
            self.min_width,
            self.max_width,
        )

        # ***** Add it to the list and try to add the border *****
        points_to_be_added = [next_point]
        if not self._add_point_and_border(points_to_be_added, direction, width):
            return False

        # It worked! Add this next set of points to the path
        path.append(points_to_be_added)

        # ***** Update the occupancy grids *****
        # The closer the point is to this point, 
        # the less occupancy can be added otherwise the walk can't progress
        for i in range(1, self.object_min_distance + 1):
            for point in path[len(path) - 1 - width - i]:
                utils.add_occupancy(self.occupancy_grid, point, i)
                utils.add_occupancy(self.tentacle_occupancy, point, i)

        return True

    # Given a starting point, direction of travel and width,
    # create a border around the point and check each point 
    # does not get too close to something else
    def _add_point_and_border(self, points, direction, width):
        # Check if the first point works
        if self._grid_check(points[0]):
            return False
        # Get the border and check each point
        borders = utils.border(direction, width)
        for border in borders:
            try:  # skip if this is out of bounds
                test_point = utils.add_points(points[0], border)
                # Don't want to intersect/touch the grid
                if not self._grid_check(test_point):
                    points.append(test_point)
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
        pass

    # Returns True if the walk should stop
    # False otherwise
    @abstractmethod
    def _stop_walk_condition(self, path):
        pass

    # In case the walk doesn't stop normally
    # with the _stop_walk_condition()
    # this determines if the walk is acceptable to use
    # Returns True if it can be used
    # False otherwise
    @abstractmethod
    def _acceptable_walk(self, path):
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
        original_distance_check = self.object_min_distance
        self.object_min_distance = 1
        success = False
        # This tentacle will be smaller than its parent
        if int(len(_path) / 2) <= int(self.min_branch_length / 2):
            self.object_min_distance = original_distance_check
            return []
        self.branch_length = random.randrange(
            int(self.min_branch_length / 2), int(len(_path) / 2)
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
        while (not new_path) and (choice_path):
            amount_tried += 1

            path = copy.copy(_path)
            start = random.choice(choice_path)
            choice_path.remove(start)

            # Remove this point and adjacent points so we can
            # do intersect or touch properly
            index = path.index(start)
            before = path[index - 1]
            # path.pop(index)
            # path.pop(index+1)

            # Get the direction that the parent branch is moving in
            # and chose a random direction that is not the direction of the parent
            # to move in, so that the branch moves away from the parent
            start_point = start[0]
            before_point = before[0]
            direction = [
                start_point[0] - before_point[0],
                start_point[1] - before_point[1],
                start_point[2] - before_point[2],
            ]

            for start_point_point in start:
                directions = (
                    [[0, 1, 0], [0, 0, 1], [0, -1, 0], [0, 0, -1]]
                    if direction[0] == 0
                    else [
                        [1, 0, 0],
                        [0, 0, 1],
                        [-1, 0, 0],
                        [0, 0, -1],
                    ]
                    if direction[0] == 0
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
                min_range = index - self.min_width - 2 if index - self.min_width - 2 > 0 else 0
                max_range = index + self.min_width + 3 if len(_path) > index + self.min_width + 3 else len(_path)
                for i in range(min_range, max_range):
                    for point in _path[i]:
                        self.grid[point[0]][point[1]][point[2]] = False

                for direction in directions:
                    # Add in this point with its border, with minimum width
                    new_points = [utils.add_points(start_point_point, direction)]
                    if not self._add_point_and_border(
                        new_points, direction, self.min_width
                    ):
                        continue
                    new_path = [new_points]


                    # Add enough to work
                    addWorked = True
                    for _ in range(self.min_width + original_distance_check):
                        # If it didn't work, go out of the for loop and try a different direction
                        if not self._try_add(direction, new_path):
                            addWorked = False
                    self.object_min_distance = original_distance_check

                    if not addWorked:
                        continue
                    success = True
                    break

            # Add the parent path points back in
            for points in _path:
                for point in points:
                    self.grid[point[0]][point[1]][point[2]] = True
        
        self.object_min_distance = original_distance_check
        
        if not success:
            return []
        return new_path
