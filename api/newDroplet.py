import math
from collections import defaultdict

MOVEMENT_TOLERANCE = 5

# paths = defaultdict(list)


def compute_euclidean_dist(p, q):
    px, py = p[0], p[1]
    qx, qy = q[0], q[1]
    diffX = abs(qx - px)
    diffY = abs(qy - py)
    return float(math.sqrt((diffX * diffX) + (diffY * diffY)))


class NewDroplet:
    def __init__(self, droplet_id, centroid, contour, color, area):
        self.dropId = droplet_id
        self.centroid = centroid
        self.contour = contour
        self.color = color
        self.area = area
        self.path = [centroid]
        # paths[self.dropId].append(centroid)

    def update_droplet(self, centroid, contour, area):
        if compute_euclidean_dist(self.centroid, centroid) > MOVEMENT_TOLERANCE:
            self.centroid = centroid
            self.contour = contour
            self.area = area
            print str(self.dropId) + " has been updated "
            # paths[self.dropId].append(centroid)
