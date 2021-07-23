from abc import ABC, abstractmethod
import itertools
from Geometry import distance3d, surrounded
import scipy.ndimage
import random
import math

class Shape(ABC):
    
    # Precondition: self has created the grid for the shape and may 
    #               or may not intersect with another object
    # Postcondition: returns None if there are no intersections, returns the 
    #               vector that will move the shape away from an intersecting 
    #               object if it does intersect.
    # This function is used in place_and_move function
    def _get_intersecting_vector(self):
        # ---------- OUTSIDE OF GRID CHECK --------------
        # Create a vector that will bring the object back into
        # the grid if it is out of bounds, otherwise set to 0
        size = self.full_grid[0][0].size
        intersecting_vector = [(size-2 - x) if (x >= size-1) 
            else (-x + 1) if (x <= 0) else 0 for x in self.center]
        
        # If not [0,0,0] then it was out of bounds
        # Nothing more to do, return vector to bring it back in
        if intersecting_vector != [0,0,0]:
            return intersecting_vector

        # -------------- INTERSECT CHECK -----------------
        # Get the intersection of the sphere (dilated to take into account touching) 
        # and other objects to see if there's any intersection/touching
        intersection = (scipy.ndimage.binary_dilation(
                        self.grid, 
                        scipy.ndimage.generate_binary_structure(3, 3), 
                        1) 
            & self.full_grid)

        # There is no intersection, we're fine
        if not intersection.any():
            return None

        # ----------- FIND VECTOR TO PUSH AWAY -----------
        # Collect all the intersecting points and edge points 
        edge_points = []
        intersecting = []
        
        # Go through the grid and add points to the lists
        for X,Y,Z in itertools.product(range(0, size), repeat=3):
            if (intersection[X][Y][Z]):
                intersecting.append([X,Y,Z])
            
            # Only an edge if it's on the grid,
            # not completely surrounded by other points
            # and satifies shape-specific edge checker
            if ((self.grid[X][Y][Z]) 
                    and (not surrounded([X,Y,Z], self.grid)) 
                    and (self._valid_edge([X,Y,Z]))):
                edge_points.append([X,Y,Z])
        
        # Cluster the points
        # Clusters should represent one intersecting object
        clusters = []
        # Loop until there is nothing left
        while intersecting:
            # Pop off a point from intersecting and add to cluster
            cluster = []
            first_p = random.choice(intersecting)
            intersecting.remove(first_p)
            cluster.append(first_p)

            # Keep looping until we have the whole cluster
            adding = True
            while adding:
                new_points = []
                
                for point in cluster:
                    # Check surrounding points 
                    # to see if they're in the cluster
                    for x,y,z in itertools.product([-1,0,1],repeat=3):
                        if intersecting.count([
                                point[0] + x, 
                                point[1] + y, 
                                point[2] + z]) > 0:
                            point = [
                                point[0] + x, 
                                point[1] + y, 
                                point[2] + z]
                            intersecting.remove(point)
                            new_points.append(point)

                adding = True if new_points else False
                # Put all our new points in the cluster
                for point in new_points:
                    cluster.append(point)

            # Finished the while loop, all points in the
            # cluster should be in the list
            clusters.append(cluster)

        # All clusters have been created
        # Find the largest distance between a bijection of
        # (1) the cluster points that lie on the shape's edge
        # (2) the edge of the cluster that is not on the shape's edge
        all_vectors = []
        for cluster in clusters:
            cluster_edge = []
            # Add all the cluster edges
            for point in cluster:
                if not surrounded(point, intersection):
                    cluster_edge.append(point)
            # Find all the shape edges that intersect 
            cluster_shape_edge = []
            for point in cluster_edge:
                if edge_points.count(point) > 0:
                    cluster_shape_edge.append(point)
            # We want the lists to not intersect
            for point in cluster_shape_edge:
                cluster_edge.remove(point)

            # There is a chance the intersection is completely inside
            # Chose random shape edge and find the intersection edge
            # that is furthest away to move the intersection away
            if not cluster_shape_edge:
                chosen_edge = random.choice(edge_points)
                largest_distance = 0
                move_vector = random.choice(cluster_edge)
                for edge in cluster_edge:
                    if distance3d(chosen_edge, edge) > largest_distance:
                        largest_distance = distance3d(chosen_edge, edge)
                        move_vector = edge
                # Vector from the intersection point to the edge
                # we want to move the intersecting object 
                # towards and past this edge
                return [chosen_edge[0] - move_vector[0],
                            chosen_edge[1] - move_vector[1],
                            chosen_edge[2] - move_vector[2]]

            # Back to the case where we do intersect the edge
            # For this cluster, we now have the lists of (1) and (2)
            # we want the longest vector of the shortest
            largest_distance = 0
            edge_vector = []
            for c_point in cluster_edge:
                # Find the shortest for this particular point
                shortest_distance = size
                local_vector = []
                for e_point in cluster_shape_edge:
                    if distance3d(c_point, e_point) < shortest_distance:
                        shortest_distance = distance3d(c_point, e_point)
                        local_vector = [e_point[0] - c_point[0],
                                        e_point[1] - c_point[1],
                                        e_point[2] - c_point[2]]
                # If it's longer than the current largest, replace
                if shortest_distance > largest_distance:
                    largest_distance = shortest_distance
                    edge_vector = local_vector
            
            all_vectors.append(edge_vector)

        # Now we have a number of vectors that 'push' 
        # our shape away from intersections
        # The direction can be got by adding them up
        # And the magnitude should be of the largest magnitude
        final_vector = []
        final_magnitude = 0
        for vector in all_vectors:
            if not final_vector:
                final_vector = vector
            else:
                final_vector = final_vector + vector
            vector_mag = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
            if vector_mag > final_magnitude:
                final_magnitude = vector_mag

        magnitude = math.sqrt(final_vector[0]**2 + final_vector[1]**2 + final_vector[2]**2)
        final_vector = [((x / magnitude) * final_magnitude) for x in final_vector]

        return final_vector

    # This function creates a shape and checks if it intersects or touches anything. 
    #   If it does, then we move it away from that other object. 
    # Precondition: self contains the following members
    #   grid:           grid with the object in it
    #   full_grid:      grid of all the objects
    #   center:         center of the object
    #   size:           size of the grids along one axis
    # Postcondition: A shape is created with no intersections with other objects. 
    #                If it was not possible, then the shape is set at not valid.
    def _place_and_move(self):
        # Create the object
        self._create_grid()

        if not self.grid.any():
            self.valid = False
            return
        
        # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
        intersecting_vector = self._get_intersecting_vector()
        
        # If it's not none, then we found something
        # Keep looping until we don't intersect
        count_max = 10   # maximum times we'll try moving
        count = 0         # times we've tried
        while intersecting_vector is not None:
            # Check if we've tried too many times
            if count is count_max:
                self.valid = False
                break
            # Remake the object since we're intersecting
            self.center = [self.center[0] + intersecting_vector[0], self.center[1] + intersecting_vector[1], self.center[2] + intersecting_vector[2]]
            self._create_grid()

            if not self.grid.any():
                self.valid = False
                return

            # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
            intersecting_vector = self._get_intersecting_vector()
            
            count += 1

    @abstractmethod
    def _create_grid(self):
        pass

    @abstractmethod
    def _valid_edge(self, point):
        pass