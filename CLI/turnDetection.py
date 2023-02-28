import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import numpy as np;
import folium;
import math;
from geopy.distance import geodesic

# If the 2 points are A(Xa,Ya) and B(Xb,Yb), the gradient of the line is:
# m = (Yb-Ya)/(Xb-Xa) — that is, vertical change divided by horizontal change.
def lineTurnDetection(c, map):
    x  = 0
    while x < len(c)-3:
        gradient1 = (c[x][1] - c[x+1][0]) / (c[x+1][1]) - (c[x][0])
        gradient2 = (c[x+1][1] - c[x+2][0]) / (c[x+2][1]) - (c[x+1][0])
        # gradient3 = (c[x+2][1] - c[x+3][0]) / (c[x+3][1]) - (c[x+2][0])
        # gradient4 = (c[x+3][1] - c[x+4][0]) / (c[x+4][1]) - (c[x+3][0])
        # gradient5 = (c[x+4][1] - c[x+5][0]) / (c[x+5][1]) - (c[x+4][0])
        # gradient6 = (c[x+5][1] - c[x+6][0]) / (c[x+6][1]) - (c[x+5][0])
        if(gradient1<0 or gradient2<0):
            tempCoords = {(c[x][0],c[x][1]),(c[x+1][0],c[x+1][1]),(c[x+2][0],c[x+2][1])}
            folium.PolyLine(tempCoords,color='blue',weight=4).add_to(map)
        x+=3

# This is the solution (be aware that your figure is misleading):
#     x1  x0 y1  y0
# A=(150−100,50−100)=(50,−50)
#     x2  x0  y0  y2
# B=(180−100,100−100)=(80,0)
# cosΘ=A⋅B|A||B|=400502–√×80=12–√
# ⇒Θ=π4

# def angle_between_vectors_degrees(u, v):
#     """Return the angle between two vectors in any dimension space,
#     in degrees."""
#     return np.degrees(
#         math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

# # The points in tuple latitude/longitude degrees space
# A = (12.92473, 77.6183)
# B = (12.92512, 77.61923)
# C = (12.92541, 77.61985)

# # Convert the points to numpy latitude/longitude radians space
# a = np.radians(np.array(A))
# b = np.radians(np.array(B))
# c = np.radians(np.array(C))

# # Vectors in latitude/longitude space
# avec = a - b
# cvec = c - b

# # Adjust vectors for changed longitude scale at given latitude into 2D space
# lat = b[0]
# avec[1] *= math.cos(lat)
# cvec[1] *= math.cos(lat)

# # Find the angle between the vectors in 2D space
# angle2deg = angle_between_vectors_degrees(avec, cvec)

def angleTurnDetection(coords, map):
    x = 0
    while x < len(coords)-3:
        # Convert the points to numpy latitude/longitude radians space
        a = np.radians(np.array(coords[x]))
        b = np.radians(np.array(coords[x+1]))
        c = np.radians(np.array(coords[x+2]))

        # Vectors in latitude/longitude space
        avec = a - b
        cvec = c - b

        # Adjust vectors for changed longitude scale at given latitude into 2D space
        lat = b[0]
        avec[1] *= math.cos(lat)
        cvec[1] *= math.cos(lat)

        # Find the angle between the vectors in 2D space
        try:
            angle2deg = np.degrees(math.acos(np.dot(avec, cvec) / (np.linalg.norm(avec) * np.linalg.norm(cvec))))
        except ValueError:
            pass

        if(angle2deg<=150):
            tempCoords = {(coords[x][0],coords[x][1]),(coords[x+1][0],coords[x+1][1]),(coords[x+2][0],coords[x+2][1])}
            folium.PolyLine(tempCoords,color='blue',weight=4).add_to(map) 
        x +=3

def velocityTurnDetection(frame, map):
    # distance = []
    velocityList = [0]
    for x in range(len(frame.latitude)-1):
            geodesicDistance = geodesic([frame.latitude[x], frame.longitude[x]],[frame.latitude[x+1], frame.longitude[x+1]]).meters
            # time = intoSeconds(frame.time[x]) -  intoSeconds(frame.time[x+1])
            time = np.datetime64(frame.time[x+1]) - np.datetime64(frame.time[x])
            # print(time)
            seconds = time / np.timedelta64(1, 's')
            # print(seconds)
            velocity = geodesicDistance/seconds
            velocityList.append(velocity)
    frame['velocity'] = velocityList
    avgVelocity = frame.velocity.mean()
    # print(avgVelocity)
    iterated = frame.iterrows()
    # print(frame.head)
    for _, x in iterated:
        if(x['velocity']<1):
            tempCoords = (x['latitude'],x['longitude'])
            folium.CircleMarker([x['latitude'],x['longitude']],color='blue',weight=4).add_to(map)
    