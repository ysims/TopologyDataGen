import numpy as np
from ripser import ripser
from persim import plot_diagrams
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import time
import math
import itertools
pi = math.pi

def PointsInCircum(r,n=100):
    return [[math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r] for x in range(0,n+1)]

def PointsInCircumSphere(r,n=10):
    return [[r * math.cos(2*pi/n*y) * math.sin(pi/n*x) , r * math.sin(2*pi/n*y) * math.sin(pi/n*x), r * math.cos(pi/n*x)] for x, y in itertools.product(range(0,n+1), range(0,n+1))]

# Create a random array of data points. The first number is the number of data points, the second is the dimension.
data = np.random.random((500,3))
# data = np.array(PointsInCircum(0.1, 100)) # Circle
# data = np.array(PointsInCircumSphere(0.1, 15)) # Sphere

# We want to time the computation - start the clock
start = time.perf_counter()
print("Begin!")

# Calculate the persistent homology
diagrams = ripser(data, maxdim=3)['dgms']

# Finish timing and print the time it took.
end = time.perf_counter()
print('Computation took ', (end-start), ' seconds')

# Plot the data points
ax = plt.axes(projection='3d')
ax.scatter3D(data[:,0], data[:,1], data[:,2])
plt.show()


# Plot the persistent homology
plot_diagrams(diagrams, show=True)