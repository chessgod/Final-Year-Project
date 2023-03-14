import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
from turnDetection import lineTurnDetection, angleTurnDetection, velocityTurnDetection;
from videoProcessing import getVidData, splitVideo, vidStart;
from api import apiData;
import timeit;


with open('./GPX/first_video.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

# getVidData("Raw Laser Sailing Footage.mp4")
splitVideo("Raw Laser Sailing Footage.mp4")
startTime = vidStart("Raw Laser Sailing Footage.mp4")


start = timeit.default_timer()
segment = gpx.tracks[0].segments[0]
dfrunInfo = pd.DataFrame([
{   'latitude': point.latitude,
    'longitude': point.longitude,
    'time': point.time,
}for point in segment.points])

stop = timeit.default_timer()
print(stop - start)

meanLat = dfrunInfo.latitude.mean()
meanLong = dfrunInfo.longitude.mean()

# windAPI = apiData(meanLat, meanLong, dfrunInfo['time'].iloc[0])

coords = [tuple(x) for x in dfrunInfo[['latitude','longitude']].to_numpy()]


# ------ UNCOMMENT TO DIVIDE DATAPOINTS BY THREE ----- 
newCoords = []
for x in coords[0::3]:
    newCoords.append(tuple(x))



routeMap = folium.Map(
    location = [meanLat, meanLong],
    zoom_start = 14,
    tiles = 'OpenStreetMap',
    width = 1024,
    height = 600,
)

# ------ UNCOMMMENT FOR CIRCLE MARKERS ------ 

# for i in coords:
#     folium.CircleMarker([i[0],i[1]], color='red', weight = 3).add_to(routeMap)

folium.PolyLine(coords,color='red',weight=3).add_to(routeMap)

# lineTurnDetection(coords, routeMap)

angleTurnDetection(coords,routeMap)

# velocityTurnDetection(dfrunInfo, routeMap)


routeMap.show_in_browser()
