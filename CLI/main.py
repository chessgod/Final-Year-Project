import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
import gpxProcessing as gp;
import videoProcessing as vp;
from api import apiData;
import timeit;

# Reading GPX file 
with open('./GPX/first_video.gpx','r',encoding='utf-8') as file:
    gpx = gpxpy.parse(file)

segment = gpx.tracks[0].segments[0]

# Loading GPX values into dataframe
# This takes quite a while, not been able to make it faster.
dfrunInfo = pd.DataFrame([
{   'latitude': point.latitude,
    'longitude': point.longitude,
    'time': point.time,
}for point in segment.points])

#Calculation to get how long the gpx data is (in time)
gpxDuration = dfrunInfo["time"].iloc[-1] - dfrunInfo["time"].iloc[0]

# Function that concatenates different clips inputted by the user
fullVideo, videoDuration = vp.combineClips()

# This ensures that "trimmedVideo" always has a value,
# as it is used on line 119. However, if the video has not been trimmed
# it will not have a value, throwing an error.
trimmedVideo = fullVideo

# Turns gpxDuration from pandas timestamp to seconds
gpxDuration = gpxDuration.total_seconds()

# Determining if video or gpx is longer
trimDecision = max(videoDuration, gpxDuration)

#Working out the difference in seconds between gpxDuration and videoDuration
offset = max(videoDuration, gpxDuration) - min(videoDuration, gpxDuration)

# Simple If statement based on which of the two is longer
if(trimDecision == videoDuration):
    print("The video is longer than the GPX file. Would you like the end or the beggining of the video to be trimmed? (e or b)")
    videoDecision = input()
    trimmedVideo = vp.videoTrim(fullVideo, videoDecision, offset)
else:
    print("The GPX is longer than the video. Would you like the end or the beggining to be trimmed? (e or b)")
    gpxDecision = input()
    dftrimmedInfo = gp.gpxTrim(dfrunInfo, gpxDecision, offset)

# These values are used later when rendering the map, so that the route is centered
meanLat = dftrimmedInfo.latitude.mean()

meanLong = dftrimmedInfo.longitude.mean()

# ----------------------- IGNORE THIS SECTION OF COMMENTED CODE  -----------------------

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

# ----------------------- END OF SECTION   -----------------------


# This extracts just the coordinates from the dataframe
coords = [tuple(x) for x in dftrimmedInfo[['latitude','longitude']].to_numpy()]


# This uses the popular library "folium" to create the map
routeMap = folium.Map(
    # This is the center point of the map
    location = [meanLat, meanLong],
    # Determines how zoomed in the map is (satellite POV)
    zoom_start = 14,
    tiles = 'OpenStreetMap',
    width = 1024,
    height = 600,
)

# ------ UNCOMMMENT FOR CIRCLE MARKERS ------ 

# for i in coords:
#     folium.CircleMarker([i[0],i[1]], color='red', weight = 3).add_to(routeMap)

# This is the code that creates the red line, showing the sail
folium.PolyLine(coords,color='red',weight=3).add_to(routeMap)

# -------------- TURN DETECTION CODE ----------------

gp.velocityTurnDetection(dftrimmedInfo, routeMap)
gp.angleTurnDetection(coords,routeMap, dftrimmedInfo)
# gp.aiTurnDetection(dfrunInfo)
# gp.aiTurnDetection_Load(dfrunInfo)

# Creates a new frame with just Turns, used in splitVideo()
turnFrame = dftrimmedInfo[dftrimmedInfo['turn'] == 1]

# Calls function that will generate the final video
vp.splitVideo(trimmedVideo,turnFrame)

# Outputs the final map to the browser
routeMap.show_in_browser()
