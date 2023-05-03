from flask import Flask, render_template, url_for, request, session, send_file;
import folium;
import sys;
import os;
import gpxpy;
import pandas as pd;
import moviepy as mp;
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

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret_key"
app.config['UPLOAD_FOLDER'] = "static/files"


@app.route('/')
def index():
    try:
        # os.remove(csvLocation())
        # os.remove(videoLocation())
        # os.remove("static/files/final.mp4")
        pass
    except:
        pass
    return render_template("index.html")

@app.route('/fileUpload', methods = ["POST", "GET"])
def fileUpload():
    if request.method == "POST":
        tempGPXfile = request.files["gpxFile"]
        videos = request.files.getlist('videoFiles')
        if tempGPXfile:
            gpxFile = tempGPXfile.read()

            # Reading GPX file 
            gpx = gpxpy.parse(gpxFile)
            segment = gpx.tracks[0].segments[0]

            # Loading GPX values into dataframe
            # This takes quite a while, not been able to make it faster.
            # print("here")
            dfrunInfo = pd.DataFrame([
            {   'latitude': point.latitude,
                'longitude': point.longitude,
                'time': point.time,
            }for point in segment.points])
            # print("past")
            dfrunInfo.to_csv(csvLocation(),index=False)

            #Calculation to get how long the gpx data is (in time)
            gpxDuration = dfrunInfo["time"].iloc[-1] - dfrunInfo["time"].iloc[0]
            gpxDuration = gpxDuration.total_seconds()
            session["gpxDuration"] = gpxDuration
            # print("GPX Duration: ", gpxDuration)

        if videos:
            # print("combining")
            fullVideo, videoDuration = vp.combineClips(videos)         
            fullVideo.write_videofile("static/files/fullVideo.mp4")
            session["videoDuration"] = videoDuration
            # print("Video Duration: ", videoDuration)
        # return dfrunInfo, gpxDuration.total_seconds()

    if gpxDuration and videoDuration:
        trimDecision = max(videoDuration, gpxDuration)
        offset = max(videoDuration, gpxDuration) - min(videoDuration, gpxDuration)
        if trimDecision==videoDuration:
            trimDecision = "video"
        else:
            trimDecision = "GPX"
        session["trimDecision"] = trimDecision
        session["offset"] = offset


    return render_template("index.html", offset=offset, trimDecision=trimDecision)

@app.route('/popUp', methods = ["POST", "GET"])
def popUp():
    types ={
        "latitude" : float,
        "longitude" : float,
    }
    if request.method=="POST":
        userTrim = request.form.get("trimType") 
        offset = session["offset"]
        trimDecision = session["trimDecision"]
        if(trimDecision=="video"):
            video = mp.VideoFileClip("static/files/fullVideo.mp4")
            trimmedVideo = vp.videoTrim(video, userTrim, offset)
            os.remove("static/files/fullVideo.mp4")
            trimmedVideo.write_videofile("static/files/fullVideo.mp4")
            # trimmedIo = session.get("fullVideo")
            
        else:
            frame = pd.read_csv(csvLocation(),  dtype=types, parse_dates=['time'])
            trimmedDf = gp.gpxTrim(frame, userTrim, offset)
            os.remove(csvLocation())
            trimmedDf.to_csv(csvLocation())
            
        return render_template("index.html", options=True, uploadText=True)


# @app.route('/videos_uploaded', methods = ["POST", "GET"])
# def videoUpload():
#     if request.method == "POST":
#         videos = request.files.getlist('videoFiles')
#         fullVideo, videoDuration = vp.combineClips(videos)

#     return render_template("index.html", fullVideo=fullVideo, videoDuration=videoDuration)

@app.route('/options_selected', methods=["POST", "GET"])
def optionSelection():

    # These values are used later when rendering the map, so that the route is centered
    # frame = session["frame"]
    # video = session["fullVideo"]
    types ={
        "latitude" : float,
        "longitude" : float,
    }
    frame = pd.read_csv(csvLocation(), dtype=types, parse_dates=['time'])
    video = mp.editor.VideoFileClip("static/files/fullVideo.mp4")
    if request.method == "POST":
        direction = request.form.get("direction")
        manouver = request.form.get("maneuver")
        clips = request.form.get("clips")

    meanLat = frame.latitude.mean()

    meanLong = frame.longitude.mean()

        # This extracts just the coordinates from the dataframe
    coords = [tuple(x) for x in frame[['latitude','longitude']].to_numpy()]


    # This uses the popular library "folium" to create the map
    routeMap = folium.Map(
        # This is the center point of the map
        location = [meanLat, meanLong],
        # Determines how zoomed in the map is (satellite POV)
        zoom_start = 14,
        tiles = 'OpenStreetMap',
        # width = 1024,
        # height = 600,
    )

    # This is the code that creates the red line, showing the sail
    folium.PolyLine(coords,color='red',weight=3).add_to(routeMap)

    # -------------- TURN DETECTION CODE ----------------

    gp.velocityTurnDetection(frame, routeMap)
    gp.angleTurnDetection(coords,routeMap, frame, direction=direction)
    # gp.aiTurnDetection(frame)
    # gp.aiTurnDetection_Load(frame)

    # Creates a new frame with just Turns, used in splitVideo()
    turnFrame = frame[frame['turn'] == 1]

    # Calls function that will generate the final video
    trainingVideo = vp.splitVideo(video,turnFrame, manouver=manouver, numVideos=clips)
    video.close()
    return render_template("output.html", video=True, map=routeMap._repr_html_())

@app.route("/download")
def download():
    return send_file(videoLocation(final=True), as_attachment=True)

def csvLocation():
    # Get the current working directory
    current_directory = os.getcwd()

    # Specify the file location relative to the current working directory
    fileLocation = os.path.join(current_directory, 'static/files', 'dataframe.csv')
    return fileLocation

def videoLocation(final=False):

    current_directory = os.getcwd()
    if final:
        fileLocation = os.path.join(current_directory, 'static/files', 'final.mp4')
    else:
        fileLocation = os.path.join(current_directory, 'static/files', 'fullVideo.mp4')
    
    return fileLocation

if __name__ == "__main__":
    app.run(debug=True)