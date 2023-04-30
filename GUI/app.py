
import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import folium;
import sys;
import os;

# Get the absolute path of the directory containing views.py
views_dir = os.path.dirname(os.path.abspath(__file__))


# Navigate up one directory to get to the my_project directory
project_dir = os.path.join(views_dir, '..')

# Navigate to the my_module directory
module_dir = os.path.join(project_dir, 'CLI')

# Add the module directory to the Python path
sys.path.append(module_dir)

import gpxProcessing as gp;
import videoProcessing as vp;
# from api import apiData;
import timeit;

def gpxDfCreation(gpxfile):

    # Reading GPX file 
    gpx = gpxpy.parse(gpxfile)
    segment = gpx.tracks[0].segments[0]

    # Loading GPX values into dataframe
    # This takes quite a while, not been able to make it faster.
    # start = timeit.default_timer()
    dfrunInfo = pd.DataFrame([
    {   'latitude': point.latitude,
        'longitude': point.longitude,
        'time': point.time,
    }for point in segment.points])
    # stop = timeit.default_timer()
    # result = stop-start
    # print("GPX frame: ", result)

    #Calculation to get how long the gpx data is (in time)
    gpxDuration = dfrunInfo["time"].iloc[-1] - dfrunInfo["time"].iloc[0]

    return dfrunInfo, gpxDuration.total_seconds()

def videoConcat(videoFiles, pbar):

    # Function that concatenates different clips inputted by the user

    fullVideo, videoDuration = vp.combineClips(videoFiles,pbar)

    return fullVideo, videoDuration
    
def timeDifference(gpxDuration, videoDuration):

    # Determining if video or gpx is longer
    trimDecision = max(videoDuration, gpxDuration)
    offset = max(videoDuration, gpxDuration) - min(videoDuration, gpxDuration)

    return offset, trimDecision

def trim(trimType, decision, offset, frame=None, fullVideo=None):
    
    if(trimType=="Video"):
        trimmedVideo = vp.videoTrim(fullVideo, decision, offset)
        return trimmedVideo
    else:
        trimmedDf = gp.gpxTrim(frame, decision, offset)
        return trimmedDf
    

def main(frame, video, manouver, direction, clips):
    # print("here")
    # Reading GPX file 
    # gpx = gpxpy.parse(gpxFile)
    # segment = gpx.tracks[0].segments[0]

    # # Loading GPX values into dataframe
    # # This takes quite a while, not been able to make it faster.
    # dfrunInfo = pd.DataFrame([
    # {   'latitude': point.latitude,
    #     'longitude': point.longitude,
    #     'time': point.time,
    # }for point in segment.points])

    # print(dfrunInfo.head)

    # fullVideo, videoDuration = vp.combineClips(videoFiles)

    # This ensures that "trimmedVideo" always has a value,
    # as it is used on line 119. However, if the video has not been trimmed
    # it will not have a value, throwing an error.
    # trimmedVideo = fullVideo 

    # # Turns gpxDuration from pandas timestamp to seconds
    # gpxDuration = gpxDuration.total_seconds()

    # # Determining if video or gpx is longer
    # trimDecision = max(videoDuration, gpxDuration)

    # #Working out the difference in seconds between gpxDuration and videoDuration
    # offset = max(videoDuration, gpxDuration) - min(videoDuration, gpxDuration)

    # # Simple If statement based on which of the two is longer

    # if(trimDecision == videoDuration):
    #     print("The video is longer than the GPX file. Would you like the end or the beggining of the video to be trimmed? (e or b)")
    #     videoDecision = input()
    #     trimmedVideo = vp.videoTrim(fullVideo, videoDecision, offset)
    # else:
    #     print("The GPX is longer than the video. Would you like the end or the beggining to be trimmed? (e or b)")
    #     gpxDecision = input()
    #     dftrimmedInfo = gp.gpxTrim(frame, gpxDecision, offset)

    # These values are used later when rendering the map, so that the route is centered
    meanLat = frame.latitude.mean()

    meanLong = frame.longitude.mean()

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

    # windAPI = apiData(meanLat, meanLong, frame['time'].iloc[0])

    # ----------------------- END OF SECTION   -----------------------


    # This extracts just the coordinates from the dataframe
    coords = [tuple(x) for x in frame[['latitude','longitude']].to_numpy()]


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

    gp.velocityTurnDetection(frame, routeMap)
    gp.angleTurnDetection(coords,routeMap, frame, direction)
    # gp.aiTurnDetection(frame)
    # gp.aiTurnDetection_Load(frame)

    # Creates a new frame with just Turns, used in splitVideo()
    turnFrame = frame[frame['turn'] == 1]

    # Calls function that will generate the final video
    trainingVideo = vp.splitVideo(video,turnFrame, manouver=manouver, numVideos=clips)

    # Outputs the final map to the browser
    return routeMap, trainingVideo
