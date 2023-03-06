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
    while x < len(c)-6:
        gradient1 = (c[x][1] - c[x+1][0]) / (c[x+1][1]) - (c[x][0])
        gradient2 = (c[x+1][1] - c[x+2][0]) / (c[x+2][1]) - (c[x+1][0])
        gradient3 = (c[x+2][1] - c[x+3][0]) / (c[x+3][1]) - (c[x+2][0])
        gradient4 = (c[x+3][1] - c[x+4][0]) / (c[x+4][1]) - (c[x+3][0])
        gradient5 = (c[x+4][1] - c[x+5][0]) / (c[x+5][1]) - (c[x+4][0])
        gradient6 = (c[x+5][1] - c[x+6][0]) / (c[x+6][1]) - (c[x+5][0])
        # print(gradient1 + gradient2 + gradient3 +gradient4 + gradient5 + gradient6)
        if(gradient1 + gradient2 + gradient3 +gradient4 + gradient5 + gradient6>0):
            tempCoords = {(c[x][0],c[x][1]),(c[x+1][0],c[x+1][1]),(c[x+2][0],c[x+2][1])}
            folium.PolyLine(tempCoords,color='blue',weight=4).add_to(map)
        x+=6

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
            folium.CircleMarker([coords[x][0],coords[x][1]],color='blue',weight=4).add_to(map) 
            # for i in range(6):
            #     folium.CircleMarker([coords[x+i][0],coords[x+i][1]],color='blue',weight=4).add_to(map)  
        x+=1

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
    lowerQuartile = frame.velocity.quantile([0.25])
    # print(lowerQuartile)
    # print(avgVelocity)
    iterated = frame.iterrows()
    # print(frame.head)
    for _, x in iterated:
        if(x['velocity']<avgVelocity):
            # tempCoords = (x['latitude'],x['longitude'])
            folium.CircleMarker([x['latitude'],x['longitude']],color='blue',weight=4).add_to(map)
            # folium.Marker([x['latitude'],x['longitude']],popup=x['velocity'],color='blue',weight=4).add_to(map)
    