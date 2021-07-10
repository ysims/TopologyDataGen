from abc import ABC
import itertools
from Geometry import distance3d, surrounded
import scipy.ndimage

class Shape(ABC):
    
    # Precondition: self has created the grid for the shape and may 
    #               or may not intersect with another object
    # Postcondition: returns None if there are no intersections, returns the 
    #               vector that will move the shape away from an intersecting 
    #               object if it does intersect.
    # This function is used in place_and_move function
    def __get_intersecting_vector(self):
        # Get the intersection of the sphere (dilated to take into account touching) 
        # and other objects to see if there's any intersection/touching
        intersection = (scipy.ndimage.binary_dilation(
                        self.grid, 
                        scipy.ndimage.generate_binary_structure(3, 3), 
                        1) 
            & self.full_grid)

        # Create a vector that will bring the object back into
        # the grid if it is out of bounds, otherwise set to 0
        intersecting_vector = [(self.size-1 - x) if (x >= self.size-1) 
            else (-x) if (x <= 0) else 0 for x in self.center]
        
        # If not [0,0,0] then it was out of bounds
        # Nothing more to do, return vector to bring it back in
        if intersecting_vector != [0,0,0]:
            return intersecting_vector

        # If there is a true point, find it
        intersecting_vector = None
        intersection_distance = self.size # we want to find the intersection closest to the center
        edge_points = []
        for X,Y,Z in itertools.product(range(0, self.size), repeat=3):
            # It's true, lets set it as our intersecting point
            if (intersection[X][Y][Z]):
                # First check if it's actually closer to the center than our previous point
                if distance3d(self.center, [X, Y, Z]) < intersection_distance:
                    intersecting_vector = [X, Y, Z]
            # We also want to collect edge points to compare with
            if self.grid[X][Y][Z]:                        # it's only an edge if it's actually in the object
                if (not surrounded([X,Y,Z], self.grid)):  # check if we're surrounded or not
                    if self.valid_edge([X,Y,Z]):          # check if this point is probably an edge
                        edge_points.append([X,Y,Z])         # add it to our list since it's an edge
        
        if not(intersecting_vector is None):
            # We want to find the edge point with the smallest distance to the intersecting point
            distance = self.size  # just set it to something larger than what we'll see first
            closest_edge = []       # the closest edge point we have
            for edge in edge_points:
                # We should check if this point has an intersection first. If it doesn't, the intersecting object isn't approaching from here
                if (not intersection[edge[0]][edge[1]][edge[2]]):
                    continue    # we shouldn't push it that way if it's not intersecting
                # If this is closer, make it our new closest edge!
                if distance3d(intersecting_vector, edge) < distance:
                    distance = distance3d(intersecting_vector, edge)
                    closest_edge = edge

            # If there isn't anything and the intersection is completely within, just push it out anywhere
            if not closest_edge:
                closest_edge = edge_points[0]

            # We should have a good vector now, so lets make it
            intersecting_vector = [closest_edge[0] - intersecting_vector[0], closest_edge[1] - intersecting_vector[1], closest_edge[2] - intersecting_vector[2]]

        return intersecting_vector

    # This function creates a shape and checks if it intersects or touches anything. 
    #   If it does, then we move it away from that other object. 
    # Precondition: self contains the following members
    #   grid:           grid with the object in it
    #   full_grid:      grid of all the objects
    #   center:         center of the object
    #   size:           size of the grids along one axis
    #   create_grid():  function that creates a grid with the object defined 
    #                   by its own class variable values, stored in 'grid'
    # Postcondition: A shape is created with no intersections with other objects. 
    #                If it was not possible, then the shape is set at not valid.

    def place_and_move(self):
        # Create the object
        self.create_grid()
        
        # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
        intersecting_vector = self.__get_intersecting_vector()
        
        # If it's not none, then we found something
        # Keep looping until we don't intersect
        count_max = 10   # maximum times we'll try moving
        count = 0         # times we've tried
        while intersecting_vector is not None:
            # Check if we've tried too many times
            if count is count_max:
                print("Failed to create object, retrying.")
                self.valid = False
                break
            # Remake the object since we're intersecting
            self.center = [self.center[0] + intersecting_vector[0], self.center[1] + intersecting_vector[1], self.center[2] + intersecting_vector[2]]
            self.create_grid()

            # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
            intersecting_vector = self.__get_intersecting_vector()
            
            count += 1