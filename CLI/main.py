import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;

with open('sail.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

runInfo = [] #This is where I will store the raw coordinate values
generalLongitude = 0 #This is to determine the general longitude of the map
generalLatitude = 0 #This determines the general latitude of the map


for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            runInfo.append({
                'latitude': point.latitude,
                'longitude': point.longitude,
                'time': point.time,
            })
            generalLongitude = generalLongitude + point.longitude
            generalLatitude = generalLatitude + point.latitude
            # if(point.longitude>generalLongitude):
            #     generalLongitude = point.longitude
            # if(point.latitude>generalLatitude):
            #     generalLatitude = point.latitude

dfrunInfo = pd.DataFrame(runInfo)
print(dfrunInfo.head(5))
# plt.figure(figsize=[14,8])
# plt.scatter(dfrunInfo['longitude'], dfrunInfo['latitude'], color='blue')
# plt.show()
generalLongitude = generalLongitude/len(runInfo)
generalLatitude = generalLatitude/len(runInfo)

coords = [tuple(x) for x in dfrunInfo[['latitude','longitude']].to_numpy()]

routeMap = folium.Map(
    location = [generalLatitude, generalLongitude],
    zoom_start = 15,
    tiles = 'OpenStreetMap',
    width = 1024,
    height = 600
)
# for i in coords:
#     folium.CircleMarker([i[0],i[1]], color='red', weight = 3).add_to(routeMap)

# folium.Marker([generalLatitude,generalLongitude]).add_to(routeMap)
folium.PolyLine(coords,color='red',weight=3).add_to(routeMap)
routeMap.show_in_browser()
