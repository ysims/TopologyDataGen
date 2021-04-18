import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import itertools

a = 0
b = 35
dim = 3
noise = 0.1

M = np.array(list(itertools.product(range(a, b), repeat=dim))).astype(np.float32)

for coord in range(len(M)):
    for point in range(len(M[coord])):
        random_noise = (np.random.random() - 0.5) * noise * 2
        M[coord][point] += random_noise

with open('data.txt', 'w') as f:
    for item in M:
        f.write("%s\n" % item)


# Plot the data points
ax = plt.axes(projection='3d')

ax.scatter3D(M[:,0], M[:,1], M[:,2])

plt.show()