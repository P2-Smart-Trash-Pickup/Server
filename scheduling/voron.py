import numpy as np

import matplotlib.pyplot as plt
points = np.array([[-4,4],[-2,2],[-4,1],[0,0],[2,2],[1,4]])
from scipy.spatial import Voronoi, voronoi_plot_2d
vor = Voronoi(points)
print(vor)
fig = voronoi_plot_2d(vor)
plt.show()
