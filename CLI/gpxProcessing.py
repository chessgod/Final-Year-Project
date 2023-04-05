import gpxpy;
import gpxpy.gpx;
import pandas as pd;
import matplotlib.pyplot as plt;
import numpy as np;
import folium;
import math;
from geopy.distance import geodesic;
import tensorflow as tf;
from sklearn.model_selection import train_test_split;
import datetime as dt;

# FUnction for trimming GPX data if longer than video
def gpxTrim(frame, decision, offset):

    offset = round(offset)
    # Turninng offset into timedelta for ease of use
    offsetDelta = dt.timedelta(seconds=offset)

    # Differentiation between end or beggining cutoff 
    # as you can see a lot of repeated code.
    if(decision == "e"):
       startTime = frame["time"].iloc[-1]
       cutoff = startTime - offsetDelta
       newFrame = frame.query("time<@cutoff")
    elif(decision == "b"):
        endTime = frame["time"].iloc[0]
        cutoff = endTime + offsetDelta
        newFrame = frame.query(f"time>@cutoff")
    return newFrame

# Failed turn detection that had to do with gradients 
# Don't bother with this, I'm only keeping it to use in the report later
# it is not used in the actual program.
def lineTurnDetection(c, map):
    x  = 0
    while x < len(c)-6:
        # Very crude code for working out line gradients
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

# The real turn detection function
def angleTurnDetection(coords, map, frame):
    x = 0 # Counter variable
    angleList = [] #Angle List that will later be added to dataframe
    turnList = [] #Turn List that will later be added to dataframe
    manouverList = [] #Manouver List that will later be added to dataframe

    # Collecting user input
    print("What was the wind direction during your sail?(N,S,E,W,NE,SE..)")
    windDirection = input()

    while x < len(coords)-3:
        # Convert the points to numpy latitude/longitude
        a = np.radians(np.array(coords[x]))
        b = np.radians(np.array(coords[x+1]))
        c = np.radians(np.array(coords[x+2]))

        # Calculate vectors between points
        aVec = a - b
        cVec = c - b

        # Adjust vectors for changed longitude scale at given latitude into 2D space
        lat = b[0]
        aVec[1] *= math.cos(lat)
        cVec[1] *= math.cos(lat)

        # Calculate the angle 
        try:
            angle2deg = np.degrees(math.acos(np.dot(aVec, cVec) / (np.linalg.norm(aVec) * np.linalg.norm(cVec))))
            
        except ValueError:
            pass
        angleList.append(angle2deg)

        # Thresholding code I will change this with full and by angles etc.
        if(angle2deg<=150):    
            
            turnList.append(1)
            # Determining type of manouver
            manouverResult = manouverType(a,b, windDirection)

            # Adding manouver to list, later added to dataframe
            manouverList.append(manouverResult)
            folium.CircleMarker([coords[x][0],coords[x][1]],color='blue',weight=4).add_child(folium.Popup(manouverResult)).add_to(map)

            # THis adds more markers to better visualise the turn, uncomment if you're curious,
            # it has no impact on performance.

            # try:
            #     for i in range(6):
            #         folium.CircleMarker([coords[x+i][0],coords[x+i][1]],color='blue',weight=4).add_to(map)  
            # except:
            #     pass
        else:
            turnList.append(0)
            manouverList.append(0)
        x+=1
    # Account for the three dropped points in while loop
    for x in range(3):
        # Don't know how to do this better, the lists are missing the last 
        # 3 elements as a result of removing them in the beggining of the while loop.
        angleList.append(0)
        turnList.append(0)
        manouverList.append(0)

    # Adding values to original dataframe 
    frame['angle'] = angleList
    frame['turn'] = turnList
    frame['manouverType'] = manouverList

# Velocity turn detection algorithm, this is now really used for velocity values,
# no real turn detection.
def velocityTurnDetection(frame, map):
    velocityList = [0]
    for x in range(len(frame.latitude)-1):
            # Tried to remove some GPS inaccuracies
            geodesicDistance = geodesic([frame.latitude[x], frame.longitude[x]],[frame.latitude[x+1], frame.longitude[x+1]]).meters
            # time = intoSeconds(frame.time[x]) -  intoSeconds(frame.time[x+1])

            # Calculating difference in time between two points
            time = np.datetime64(frame.time[x+1]) - np.datetime64(frame.time[x])

            # Converting to seconds
            seconds = time / np.timedelta64(1, 's')

            # Velocity calculation
            velocity = geodesicDistance/seconds

            velocityList.append(velocity)
    frame['velocity'] = velocityList

    # ----------- The below section was for turn detection, Ill use it in report, but not in program ---------

    # avgVelocity = frame.velocity.mean()
    # # print(avgVelocity)
    # lowerQuartile = frame.velocity.quantile([0.25])
    # # print(lowerQuartile)
    # # print(avgVelocity)
    # iterated = frame.iterrows()
    # print(frame.head)
    # for _, x in iterated:
    #     if(x['velocity']<avgVelocity):
    #         # tempCoords = (x['latitude'],x['longitude'])
    #         folium.CircleMarker([x['latitude'],x['longitude']],color='blue',weight=4).add_to(map)
    #         # folium.Marker([x['latitude'],x['longitude']],popup=x['velocity'],color='blue',weight=4).add_to(map)

    # ---------- END OF SECTION --------------


# Function for determining turn type
def manouverType(first, second, direction):
    # code for working out if tack or gybe

    # Dictionary with degree variables for compass directions
    compassDegrees = {
        "N": 90,
        "NE": 45,
        "E": 0,
        "SE": -45,
        "S": -90,
        "SW": -135,
        "W": 180,
        "NW": 135
    }

    # Calculate changes in latitude and longitude

    latChange = first[0] - second[0]
    lonChange = first[1] - second[1]

    #Calculation for angle difference between heading and wind direction

    headingDiffernce = math.degrees(math.atan2(lonChange, latChange)) - compassDegrees[direction]

    if abs(headingDiffernce) > 90:
        # The boat has gybed if the headingDiffernce is greater than 90 degrees
        if headingDiffernce < 0:
            return "GP"
        else:
            return "GS"
    else:
        # The boat has tacked if the headingDiffernce is less than or equal to 90 degrees
        if headingDiffernce < 0:
            return "TP"
        else:
            return "TS"

# Failed attempt at aiTurnDetection, only being kept for report
# You're welcome to take a look, it's my first attempt at working with AI
# and likely riddled with issues.
def aiTurnDetection(df):
    model = tf.keras.models.Sequential()
    xVals = df.drop(['turn','time'], axis=1)
    # xVals['time'] = xVals['time'].astype("str")
    yVals = df['turn']

    x_train, x_test, y_train, y_test = train_test_split(xVals,yVals,test_size=0.2)
    x_train = np.asarray(x_train).astype(np.float32)
    y_train = np.asarray(y_train).astype(np.float32)
    model.add(tf.keras.layers.Dense(64, input_shape=x_train.shape[1:], activation = 'sigmoid'))
    model.add(tf.keras.layers.Dense(64, activation='sigmoid'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer="adam", loss = "binary_crossentropy", metrics=["accuracy"])

    model.fit(x_train, y_train, epochs=500, verbose=0)

    print("Training data results: ")
    model.evaluate(x_train, y_train)
    # print("Training data results: " + results)
    model.save("laser-in.h5")

# Function to load trained model on to unseen data
# Same as above, probably riddled with issues.
def aiTurnDetection_Load(df):
    model = tf.keras.models.load_model("laser-in.h5")
    xVals = df.drop(['turn','time'], axis=1)
    # xVals['time'] = xVals['time'].astype("str")
    yVals = df['turn']

    x_train, x_test, y_train, y_test = train_test_split(xVals,yVals,test_size=0.2)
    try:
        x_test = np.asarray(x_test).astype(np.float32)
        y_test = np.asarray(y_test).astype(np.float32)
    except ValueError as e:
        if str(e) == "could not convert string to float":
            pass
        else:
            print(e)

    model.fit(x_test, y_test, epochs=500, verbose=0)

    print("Unseen data: ")
    model.evaluate(x_test, y_test)