import numpy as np
import itertools
import random
import math
from operator import add
import copy
import scipy.ndimage

from Geometry import rotate_grid, distance3d, intersect_or_touch, surrounded, rotate_object

# ----------------- USED FOR MAKING SHAPES -----------------------

# Given a shape and the full grid, find the vector that will move the shape away from intersection/touching
# Used in place_and_move function
def get_intersecting_vector(object):
    dilation_structure = scipy.ndimage.generate_binary_structure(3, 3)

    # Get the intersection of the sphere (dilated to take into account touching) and other objects to see if there's any intersection/touching
    intersection = scipy.ndimage.binary_dilation(object.grid, dilation_structure, 1) & object.full_grid

    # Have to initialise it somehow
    intersecting_vector = [0,0,0]
    # Lets see if we've gone out of bounds
    for index,x in enumerate(object.center):
        if x >= object.size-1:
            intersecting_vector[index] = object.size-1 - x
        if x <= 0:
            intersecting_vector[index] = -x
    # If we did find we're out of bounds, just return what we've found
    if intersecting_vector != [0,0,0]:
        return intersecting_vector

    # If there is a true point, find it
    intersecting_vector = None
    intersection_distance = object.size # we want to find the intersection closest to the center
    edge_points = []
    for X,Y,Z in itertools.product(range(0, object.size), repeat=3):
        # It's true, lets set it as our intersecting point
        if (intersection[X][Y][Z]):
            # First check if it's actually closer to the center than our previous point
            if distance3d(object.center, [X, Y, Z]) < intersection_distance:
                intersecting_vector = [X, Y, Z]
        # We also want to collect edge points to compare with
        if object.grid[X][Y][Z]:                        # it's only an edge if it's actually in the object
            if (not surrounded([X,Y,Z], object.grid)):  # check if we're surrounded or not
                if object.valid_edge([X,Y,Z]):          # check if this point is probably an edge
                    edge_points.append([X,Y,Z])         # add it to our list since it's an edge
    
    if not(intersecting_vector is None):
        # We want to find the edge point with the smallest distance to the intersecting point
        distance = object.size  # just set it to something larger than what we'll see first
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

# This function is a generic function for any shape, where we create the shape and then see if it intersects or touches anything
# If it does, then we move it away from that other object. 
# object: an instance of a shape that has a
#   grid:           grid with the object in it
#   full_grid:      grid of all the objects
#   center:         center of the object
#   size:           size of the grids along one axis
#   greate_grid():  function that creates a grid with the object defined by its own class variable values, stored in 'grid'
def place_and_move(object):
    # Create the object
    object.create_grid()
    
    # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
    intersecting_vector = get_intersecting_vector(object)
    
    # If it's not none, then we found something
    # Keep looping until we don't intersect
    count_max = 10   # maximum times we'll try moving
    count = 0         # times we've tried
    while intersecting_vector is not None:
        # Check if we've tried too many times
        if count is count_max:
            print("Failed to create object, retrying.")
            object.valid = False
            break
        # Remake the object since we're intersecting
        object.center = [object.center[0] + intersecting_vector[0], object.center[1] + intersecting_vector[1], object.center[2] + intersecting_vector[2]]
        object.create_grid()

        # Get the vector that will move us away from intersecting or touching objects (or None if not intersecting/touching)
        intersecting_vector = get_intersecting_vector(object)
        
        count += 1

# ------------------ SHAPES ----------------------

# -------- SPHEROID ---------
class Sphere(object):
    # center: center of the sphere
    # radius: radius of the sphere
    # size: how big the voxel grid is
    def __init__(self, full_grid, center, radius, size):
        # Check we're not starting in an invalid location
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set sphere information
        self.center = center
        self.radius = radius
        self.full_grid = full_grid
        self.valid = True
        self.size = size
        
        place_and_move(self)
        
    # Make a random spheroid
    @classmethod
    def random(cls, grid, size):
        center = (random.randrange(5, size-5, 1), random.randrange(5, size-5, 1), random.randrange(5, size-5, 1))
        radius = [random.randrange(3, 6, 1), random.randrange(3, 6, 1), random.randrange(3, 6, 1)]
        return cls(grid, center, radius, size)

    def create_grid(self):
        # Create a spheroid
        x, y, z = np.indices((self.size, self.size, self.size))
        self.grid = ((pow(x - self.center[0],2) / pow(self.radius[0],2)) \
            + (pow(y - self.center[1],2) / pow(self.radius[1],2)) \
            + (pow(z - self.center[2], 2) / pow(self.radius[2],2))) <= 1

    # This only gets called if it's not surrounded - there's no other things to check for a ball
    def valid_edge(self, point):
        return True

# --------- TORUS ----------
class Torus(object):
    # Make a specific torus
    def __init__(self, full_grid, center, major_radius, minor_radius, rotation, size):
        # Check we can even go here in the first place
        if intersect_or_touch(center, full_grid):
            self.valid = False
            return

        # Set torus information
        self.full_grid = full_grid
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.size = size
        self.valid = True

        place_and_move(self)

        if self.valid:
            print("CENTER: ", self.center)

        # place_and_move uses a grid that is plugged up for intersection checking - in the end, we don't want this so just make the torus normally
        x,y,z = np.indices((size, size, size))
        self.grid = pow(np.sqrt((x - self.center[0])**2 + (y - self.center[1])**2) - self.major_radius, 2) + (z - self.center[2])**2 <= self.minor_radius ** 2
        rotate_object(self, self.grid)
        
    # Make a random torus
    @classmethod
    def random(cls, full_grid, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        major_radius = random.randrange(4, int(size/8), 1)
        minor_radius = random.randrange(2, major_radius-1, 1)
        return cls(full_grid, center, major_radius, minor_radius, rotation, size)

    # This will get the circle that 'plugs' up the torus, to prevent tunnels going through
    def get_disc(self):
        x,y,z = np.indices((self.size, self.size, self.size))
        disc = (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0])**2 + (y - self.center[1])**2 <= self.major_radius ** 2)
        rotate_object(self, disc)
        return disc

    # Function required for place_and_move function
    def create_grid(self):
        # Make a voxelised torus and rotate it
        x,y,z = np.indices((self.size, self.size, self.size))
        self.grid = pow(np.sqrt((x - self.center[0])**2 + (y - self.center[1])**2) - self.major_radius, 2) + (z - self.center[2])**2 <= self.minor_radius ** 2
        rotate_object(self, self.grid)

        # Since this grid is used to check intersections, add in the disc so we don't get things going through the torus
        self.grid = self.grid | self.get_disc()

    # We don't want this to be an edge inside the middle of the torus
    def valid_edge(self, point):
        if distance3d(point, self.center) <= self.major_radius:
            return False    # it's in the inner portion of the torus, so it's not a valid edge
        return True

# A 2-torus
class Torus2(object):
    # Make a specific torus
    def __init__(self, full_grid, center, major_radius, minor_radius, rotation, size):
        # Set torus information
        self.full_grid = full_grid
        self.center = center
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.rotation = rotation
        self.size = size
        self.valid = True

        # Save the rotated grid so we don't have to do it every time
        self.r_x, self.r_y, self.r_z = rotate_grid(self.size, self.rotation, self.center)

        # Find a center that works
        place_and_move(self)

        # Make the grid properly now that we've got a valid center
        torus1 = pow(np.sqrt((self.r_x - self.center[0])**2 + (self.r_y - self.center[1])**2) - self.major_radius, 2) + (self.r_z - self.center[2])**2 <= self.minor_radius ** 2
        torus2 = pow(np.sqrt((self.r_x - self.center[0] + self.major_radius*2)**2 + (self.r_y - self.center[1])**2) - self.major_radius, 2) + (self.r_z - self.center[2])**2 <= self.minor_radius ** 2
        self.grid = torus1 | torus2
        
    # Make a random torus
    @classmethod
    def random(cls, full_grid, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        major_radius = random.randrange(4, int(size/6), 1)
        minor_radius = random.randrange(2, major_radius-1, 1)
        return cls(full_grid, center, major_radius, minor_radius, rotation, size)

    # When creating the grid, plug up the torus so place and move can detect if there's anything going through the torus
    def create_grid(self):
        torus1 = pow(np.sqrt((self.r_x - self.center[0])**2 + (self.r_y - self.center[1])**2) - self.major_radius, 2) + (self.r_z - self.center[2])**2 <= self.minor_radius ** 2
        torus2 = pow(np.sqrt((self.r_x - self.center[0] + self.major_radius*2)**2 + (self.r_y - self.center[1])**2) - self.major_radius, 2) + (self.r_z - self.center[2])**2 <= self.minor_radius ** 2
        self.grid = torus1 | torus2 | self.get_disc()

    # This will get the circle that 'plugs' up the torus, to prevent tunnels going through
    def get_disc(self):
        x,y,z = rotate_grid(self.size, self.rotation, self.center)
        disc1 = (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0])**2 + (y - self.center[1])**2 <= self.major_radius ** 2)
        disc2 = (z > self.center[2]-1) & (z < self.center[2] + 1) & ((x - self.center[0] + self.major_radius * 2)**2 + (y - self.center[1])**2 <= self.major_radius ** 2)
        return disc1 | disc2

    # Only valid if it's not in the inner part of either torus
    def valid_edge(self, point):
        # Can't be inside the first torus
        if distance3d(point, self.center) <= self.major_radius:
            return False
        # Can't be inside the second torus
        second_center = [(x + self.major_radius*2) for x in self.center]
        if distance3d(point, second_center) <= self.major_radius:
            return False
        return True


# This object represents a sphere with a sphere-shaped hole inside it
class Island(object):
    # center: center of the island
    # outer radius: radius of the outer sphere
    # inner radius: radius of the inner sphere
    # outer amplitude: how much 'wiggle' to add to the outer sphere
    # inner amplitude: how much 'wiggle' to add to the inner sphere
    # rotation: a list of three rotations that are x,y,z axis rotations and rotated in that order
    # size: how big the voxel grid is
    def __init__(self, center, outer_radius, inner_radius, rotation, size):
        # Set sphere information
        self.center = center
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.rotation = rotation

        # Find a center that works
        place_and_move(self)

        # Make a rotated grid and use it to make a voxelised sphere with a hole in the middle (island)
        x, y, z = np.indices((self.size, self.size, self.size))
        self.grid = ((pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) <= outer_radius ** 2) \
            & ((pow(x - center[0], 2) + pow(y - center[1], 2) + pow(z - center[2], 2)) >= inner_radius ** 2)

    # Make a random island
    @classmethod
    def random(cls, size):
        rotation = [random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi), random.uniform(0, 2*math.pi)]
        center = [random.randrange(1, size-1, 1), random.randrange(1, size-1, 1), random.randrange(1, size-1, 1)]
        outer_radius = random.randrange(4, int(size/6), 1)
        inner_radius = random.randrange(2, outer_radius-1, 1)
        return cls(center, outer_radius, inner_radius, rotation, size)

    # Make this as a ball for finding a good center, or we might trap an object inside...
    def create_grid(self):
        # Create a sphere
        x, y, z = np.indices((self.size, self.size, self.size))
        self.grid = (pow(x - self.center[0],2) + pow(y - self.center[1],2) + pow(z - self.center[2], 2)) <= pow(self.outer_radius, 2)

    # Only valid if it's not in the inside cavity
    def valid_edge(self, point):
        if distance3d(point, self.center) <= self.inner_radius:
            return False
        return True

class Tunnel(object):
    # Parameters
    # start: coordinate where the tunnel starts
    # size: size of the voxel grid
    # objects: list of objects for the tunnel to avoid
    # Description
    # Given a starting position on the border, make a tunnel from this point to some other point on the border 
    # Any border point should not intersect with an object since object cannot be on the border
    def __init__(self, start, size, objects, border):
        # Make a grid with just this starting point
        x, y, z = np.indices((size, size, size))
        grid = (x > size)   # False grid
        current_point = start
        # Find the forward direction
        forward = [0,0,0]
        for i in range(len(current_point)):
            if current_point[i] == 0:
                forward[i] = 1
            elif current_point[i] == size-1:
                forward[i] = -1

        # Add forward point
        previous_point = current_point
        current_point = list(map(add, forward, current_point))
        grid[current_point[0]][current_point[1]][current_point[2]] = True

        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        # Loop while we've not hit the border
        while (not border[current_point[0]][current_point[1]][current_point[2]]):
            point_added = False
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                if not self.tunnel_intersect(copy.copy(grid), list(map(add, direction, current_point)), current_point, previous_point, objects):
                    previous_point = current_point
                    current_point = list(map(add, direction, current_point))
                    grid[current_point[0]][current_point[1]][current_point[2]] = True
                    point_added = True
                    break
            # We've reached a point where nowhere will work!
            if not point_added:
                self.valid = False
                return
        self.valid = True
        self.grid = grid

    def tunnel_intersect(self, grid, new_point, old_point, old_old_point, objects):
        # Check if we can even move to this point
        # old_point was already checked last time, so should be good
        # This will stop us going back on ourselves as well, ie old == new
        try:
            if grid[new_point[0]][new_point[1]][new_point[2]]:
                return True
        except:
            return True

        # We will always be accused of touching the grid if the previous point is there
        grid[old_point[0]][old_point[1]][old_point[2]] = False
        grid[old_old_point[0]][old_old_point[1]][old_old_point[2]] = False

        # Check if there are any objects around this point
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                # Check if there are other objects around
                if objects[new_point[0] + x][new_point[1] + y][new_point[2] + z]:
                    return True
                # Check if we're about to loop back on ourselves
                if grid[new_point[0] + x][new_point[1] + y][new_point[2] + z]:
                    return True
            except:
                continue
        return False

    # Make a random tunnel
    @classmethod
    def random(cls, size, objects, border):
        # Create a random start position on a face
        start = [random.randrange(2,size-2,1) for i in range(0,3)]
        start[random.randrange(0,3,1)] = 0 if random.randrange(0,2,1) == 0 else size-1
        return cls(start, size, objects, border)

# -------- I don't know what this is - sphere with tunnels coming off it ------------
class Tentacle(object):
    def __init__(self, grid, size, num_tentacles):
        self.sphere = Sphere.random(grid, size)
        while not self.sphere.valid:
            self.sphere = Sphere.random(grid, size)
        self.grid = self.sphere.grid
        self.full_grid = grid
        self.size = size
        self.num_tentacles = num_tentacles
        self.valid = True

        # We will make a 'tentacle' going off from one of the edges
        edges = []
        for X,Y,Z in itertools.product(range(0, self.size), repeat=3):
            if self.sphere.grid[X][Y][Z]:
                directions = [[1,0,0],[0,1,0],[0,0,1],[-1,0,0],[0,-1,0],[0,0,-1]]   # lets not go diagonal
                for direction in directions:
                    try:    # skip if this is out of bounds
                        if not grid[X + direction[0]][Y + direction[1]][Z + direction[2]]:  # if it's empty, we're not surrounded
                            edges.append([X,Y,Z])   # is an edge if it's a sphere point and isn't surrounded by other sphere points
                    except:
                        continue

        if not edges:
            print("No edges, something is wrong")
            self.valid = False
            return

        for _ in range(num_tentacles):
            # Pop a random edge point off the list
            point = random.choice(edges)
            self.make_tentacle(point)
            while not self.tentacle_valid:
                point = random.choice(edges)
                self.make_tentacle(point)
            edges.remove(point)

    # Make a random octopus!
    @classmethod
    def random(cls, grid, size):
        # Create a random start position on a face
        num_tentacles = random.randrange(10,30)
        return cls(grid, size, num_tentacles)

    # We want to make a tentacle that doesn't touch anything, including the boundary
    # It can branch if it wants to
    def make_tentacle(self, point):
        self.tentacle_valid = True  # lets be optimistic for now
        # Lets put a random limit on the length of the tentacle
        # TODO: hardcoded values ew
        length = random.randrange(20, 50, 1)
        
        # Add all possible movement directions
        movement_direction = [] # list of value movements
        for x,y,z in itertools.permutations([1,0,0],3):
            movement_direction.append([x,y,z])
            movement_direction.append([-x,-y,-z])       
        movement_direction.sort()
        movement_direction = list(movement_direction for movement_direction,_ in itertools.groupby(movement_direction)) # remove duplicates

        next_point = []
        for x,y,z in itertools.product([-1,0,1],repeat=3):
            try:    # skip if this is out of bounds
                if not self.grid[point[0] + x][point[1] + y][point[2] + z]:
                    next_point = [point[0] + x, point[1] + y, point[2] + z]
                    break   # We've found something, so don't keep looking
            except:
                continue

        if not next_point:
            self.tentacle_valid = False
            print("Something went wrong.")
            return

        # next_point: a point on the tentacle, not added yet since we don't want to detect a collision with it
        current_length = 1  # to tell when we should end the while loop

        while current_length < length:
            print("length ", current_length)
            random.shuffle(movement_direction) # shuffle so we don't always go the same way
            for direction in movement_direction:
                new_point = list(map(add, direction, next_point))
                # If we don't intersect or touch anything, then move here
                if not intersect_or_touch(new_point, self.grid):
                    self.grid[next_point[0], next_point[1], next_point[2]] = True
                    next_point = new_point
                    current_length += 1
                    break   # Don't keep going with the for loop

            # If we get to this point, we weren't able to move
            # See if this was a decent enough try, otherwise just return false
            if (length < 15):
                self.tentacle_valid = False
                print("Didn't work...")
                return
            
            # Still need to break from the while loop
            else:
                break
            
        self.grid[next_point[0], next_point[1], next_point[2]] = True    # we need to set this true in the end
