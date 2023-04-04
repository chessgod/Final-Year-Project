import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
import gpxProcessing as gp;
import videoProcessing as vp;
from api import apiData;
import timeit;


with open('./GPX/first_video.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

segment = gpx.tracks[0].segments[0]

dfrunInfo = pd.DataFrame([
{   'latitude': point.latitude,
    'longitude': point.longitude,
    'time': point.time,
}for point in segment.points])

gpxDuration = dfrunInfo["time"].iloc[-1] - dfrunInfo["time"].iloc[0]

meanLat = dfrunInfo.latitude.mean()

meanLong = dfrunInfo.longitude.mean()

fullVideo, videoDuration = vp.combineClips()

gpxDuration = gpxDuration.total_seconds()

trimDecision = max(videoDuration, gpxDuration)

offset = max(videoDuration, gpxDuration) - min(videoDuration, gpxDuration)


if(trimDecision == videoDuration):
    print("The video is longer than the GPX file. Would you like the end or the beggining of the video to be trimmed? (e or b)")
    videoDecision = input()
    trimmedVideo = vp.videoTrim(fullVideo, videoDecision, offset)
else:
    print("The GPX is longer than the video. Would you like the end or the beggining to be trimmed? (e or b)")
    gpxDecision = input()
    dftrimmedInfo = gp.gpxTrim(dfrunInfo, gpxDecision, offset)


# temp = dftrimmedInfo["time"].iloc[-1] - dftrimmedInfo["time"].iloc[0]
# print(videoDuration)
# print(temp.total_seconds())

# print(videoDuration)
# print(trimmedVideo.duration)
# print(gpxDuration.total_seconds())
# print(videoDuration)
# getVidData(fullVideo)
# start1 = timeit.default_timer()
# splitVideo("Footage/GH010056.MP4")
# stop1 = timeit.default_timer()
# ans = stop1-start1
# print("Video: ", ans)
# start = timeit.default_timer()

# stop = timeit.default_timer()
# print(stop - start)

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
gp.velocityTurnDetection(dfrunInfo, routeMap)
gp.angleTurnDetection(coords,routeMap, dfrunInfo)
# gp.aiTurnDetection(dfrunInfo)
# gp.aiTurnDetection_Load(dfrunInfo)

# print(dfrunInfo.head)
routeMap.show_in_browser()
