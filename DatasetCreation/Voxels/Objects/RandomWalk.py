from abc import ABC, abstractmethod
import copy
import itertools
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
            print("Something went wrong, " 
                "couldn't find a start position.")
            return False

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        # Remove duplicates
        movement_direction = list(
            movement_direction for movement_direction,
            _ in itertools.groupby(movement_direction))

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
                new_point = list(map(add, 
                                    direction, 
                                    all_points[len(all_points) - 1]))
                if self._allowed_point(new_point, all_points):
                    all_points.append(new_point)
                    # Add onto the grid the point from two runs ago
                    if len(all_points) > 2:
                        to_add = all_points[len(all_points) - 3]
                        self.grid[to_add[0], to_add[1], to_add[2]] = True
                    point_added = True
                    break   # Don't keep going with the for loop
            
            # If a point wasn't added
            # see if this was a decent enough try
            # otherwise just return false
            if not point_added:
                if (not self._acceptable_walk(all_points)):
                    # Remove anything we added because we don't want it anymore
                    for point in all_points:
                        self.grid[point[0], point[1], point[2]] = False
                    return False
                else:
                    break
        
        # The last two points won't be there, 
        # add everything in the walk to the grid
        for point in all_points:
            self.grid[point[0], point[1], point[2]] = True

        if not self.branching:
            # Nothing seemed to go wrong and we 
            # don't want to branch so return true
            return True

        if not self.valid:
            return False

        print("valid?", self.valid)

        # Loop until there are no more paths to 
        # check for branching
        paths = []
        paths.append(copy.copy(all_points))
        while paths:
            num_branch = self._num_branches(paths[0])
            if num_branch is 0: 
                paths.remove(paths[0])
                continue
            # print("len paths:", len(paths), num_branch)

            while num_branch > 0:
                print(num_branch, len(paths))
                # print("num branches", num_branch, len(paths[0]))
                all_points = self._branch_start(paths[0])
                if not all_points:
                    break
                # Do as before and create the path
                while not self._stop_walk_condition(all_points):
                    # print("walkin")
                    # print(len(all_points))
                    point_added = False
                    random.shuffle(movement_direction)
                    for direction in movement_direction:
                        # Add the direction and the last point
                        new_point = list(map(add, 
                                            direction, 
                                            all_points[len(all_points) - 1]))
                        if self._allowed_point(new_point, all_points):
                            all_points.append(new_point)
                            # Add onto the grid the point from two runs ago
                            if len(all_points) > 2:
                                to_add = all_points[len(all_points) - 3]
                                self.grid[to_add[0], to_add[1], to_add[2]] = True
                            # print("added a point")
                            point_added = True
                            break   # Don't keep going with the for loop
            
                    # If a point wasn't added
                    # see if this was a decent enough try
                    # otherwise just return false
                    if not point_added:
                        # print("didn't add a point :(")
                        if (not self._acceptable_walk(all_points)):
                            # print("walk wasn't ok...")
                            # print("not acceptable")
                            # Remove anything we added because we don't want it anymore
                            for point in all_points:
                                self.grid[point[0], point[1], point[2]] = False
                        break

                # The last two points won't be there, 
                # add everything in the walk to the grid
                # print("everything was fine!")
                for point in all_points:
                    self.grid[point[0], point[1], point[2]] = True
                # Successfully made a branch
                num_branch -= 1
                if len(all_points) >= self.min_tentacle_length:
                    # print("long boi!", len(all_points))
                    paths.append(copy.copy(all_points))
            # print("done with this path")
            paths.remove(paths[0])
        # print("done with the tentacle")
        self.valid = True
        return True

    # Determines a start location for the walk
    # and returns the first point in the walk
    @abstractmethod
    def _get_start(self):
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

    # True if this point is allowed
    # to be added to the walk
    # False otherwise
    @abstractmethod
    def _allowed_point(self, new_point):
        pass

    # Given the path, how many times will we branch from it?
    @abstractmethod
    def _num_branches(self, path):
        pass

    # Find a point to branch from on the path
    # and return the beginning of the new path
    @abstractmethod
    def _branch_start(path):
        pass
