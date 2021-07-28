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
        
        # If it wasn't successful, just return
        if not self._walk(all_points):
            for point in all_points:
                self.grid[point[0], point[1], point[2]] = False
            return False

        # The last two points won't be there, 
        # add everything in the walk to the grid
        for point in all_points:
            self.grid[point[0], point[1], point[2]] = True

        # Nothing seemed to go wrong and we 
        # don't want to branch so return true
        if not self.branching:
            return True

        # Loop until there are no more paths to 
        # check for branching
        paths = []
        paths.append(copy.copy(all_points))
        while paths:
            # Find out how many branches should be made
            num_branch = self._num_branches(paths[0])
            if num_branch is 0: 
                paths.remove(paths[0])
                continue

            # Loop while we have branches to create
            while num_branch > 0:
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
                if not self._walk(all_points):
                    for point in all_points:
                        self.grid[point[0], point[1], point[2]] = False
                    continue

                # The last two points won't be there, 
                # add everything in the walk to the grid
                for point in all_points:
                    self.grid[point[0], point[1], point[2]] = True

                # Successfully made a branch
                num_branch -= 1
                paths.append(copy.copy(all_points))

            # Finished adding all the branches to this path 
            paths.remove(paths[0])
        
        return True


    def _walk(self, all_points):
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
