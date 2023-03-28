import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
import turnDetection as td;
from videoProcessing import getVidData, splitVideo, vidStart;
from api import apiData;
import timeit;


with open('./GPX/laser-in.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

# getVidData("Raw Laser Sailing Footage.mp4")
start1 = timeit.default_timer()
# splitVideo("Footage/GH010056.MP4")
stop1 = timeit.default_timer()
ans = stop1-start1
print("Video: ", ans)
# startTime = vidStart("Raw Laser Sailing Footage.mp4")


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
# newCoords = []
# for x in coords[0::3]:
#     newCoords.append(tuple(x))


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
td.velocityTurnDetection(dfrunInfo, routeMap)
td.angleTurnDetection(coords,routeMap, dfrunInfo)
# td.aiTurnDetection(dfrunInfo)
td.aiTurnDetection_Load(dfrunInfo)
routeMap.show_in_browser()
