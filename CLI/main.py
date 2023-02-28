import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
from turnDetection import lineTurnDetection, angleTurnDetection, velocityTurnDetection;
import timeit;


with open('Morning_Sail-2.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

runInfo = [] #This is where I will store the raw coordinate values
generalLongitude = 0 #This is to determine the general longitude of the map
generalLatitude = 0 #This determines the general latitude of the map
# start = timeit.default_timer()
segment = gpx.tracks[0].segments[0]
dfrunInfo = pd.DataFrame([
{   'latitude': point.latitude,
    'longitude': point.longitude,
    'time': point.time,
}for point in segment.points])

# stop = timeit.default_timer()
# print(stop - start)

# for _, x in dfrunInfo.iterrows():
#     # print(x['latitude'])
#     # print(x['longitude'])
#     generalLatitude = generalLatitude+ x['latitude']
#     generalLongitude = generalLongitude + x['longitude']



# for track in gpx.tracks:
#     for segment in track.segments:
#         for point in segment.points:
#             runInfo.append({
#                 'latitude': point.latitude,
#                 'longitude': point.longitude,
#                 'time': point.time,
#             })
#             generalLongitude = generalLongitude + point.longitude
#             generalLatitude = generalLatitude + point.latitude

# dfrunInfo = pd.DataFrame(runInfo)
# print(dfrunInfo.head(5))
# plt.figure(figsize=[14,8])
# plt.scatter(dfrunInfo['longitude'], dfrunInfo['latitude'], color='blue')
# plt.show()


coords = [tuple(x) for x in dfrunInfo[['latitude','longitude']].to_numpy()]
i = 0
while i < len(coords)-3:
    print(coords[i])
    newCoords = coords[i]
    i+=3

# coords and dfrunInfo are the same size, they can be used to index each other for turn color

routeMap = folium.Map(
    location = [dfrunInfo.latitude.mean(), dfrunInfo.longitude.mean()],
    zoom_start = 14,
    tiles = 'OpenStreetMap',
    width = 1024,
    height = 600
)

for i in newCoords:
    folium.CircleMarker([i[0],i[1]], color='red', weight = 3).add_to(routeMap)

# folium.Marker([generalLatitude,generalLongitude]).add_to(routeMap)
# folium.PolyLine(coords,color='red',weight=3).add_to(routeMap)
# lineTurnDetection(coords, routeMap)
angleTurnDetection(newCoords,routeMap)
# velocityTurnDetection(dfrunInfo, routeMap)

routeMap.show_in_browser()
