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

# If the 2 points are A(Xa,Ya) and B(Xb,Yb), the gradient of the line is:
# m = (Yb-Ya)/(Xb-Xa) — that is, vertical change divided by horizontal change.
tacksDict = [{}]
gybesDict = [{}]
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

def angleTurnDetection(coords, map, frame):
    x = 0
    angleList = []
    turnList = []
    manouverList = []

    print("What was the wind direction during your sail?(N,S,E,W,NE,SE..)")
    windDirection = input()

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
            # print(angle2deg)
            pass
        angleList.append(angle2deg)
        if(angle2deg<=150):    
            # manouver = manouverType(coords[x],coords[x+1],coords[x+2])
            turnList.append(1)
            # Determining type of manouver
            manouverResult = manouverType(a,b, windDirection)

            # Adding manouver to list, later added to dataframe
            manouverList.append(manouverResult)
            folium.CircleMarker([coords[x][0],coords[x][1]],color='blue',weight=4).add_child(folium.Popup(manouverResult)).add_to(map)

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
        angleList.append(0)
        turnList.append(0)
        manouverList.append(0)

    # Adding values to original dataframe 
    frame['angle'] = angleList
    frame['turn'] = turnList
    frame['manouverType'] = manouverList

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


def manouverType(first, second, direction):
    # code for working out if tack or gybe
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