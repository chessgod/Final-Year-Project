import streamlit as st
from streamlit_folium import st_folium
import app as a
import moviepy;
import time;
import pandas as pd;
from streamlit_modal import Modal;

allUploaded = False
videoModal = Modal(title="Video Modal",key="1")
gpxModal = Modal(title= "GPX Modal",key="2")
# Upload file #
st.sidebar.header('Upload GPX files here!')
gpxFiles = st.sidebar.file_uploader("GPX files here", type=['gpx'])

st.sidebar.header('Upload your files here!')
videoFiles = st.sidebar.file_uploader("Video Files here", type=['mov', 'mp4'], accept_multiple_files=True)


st.title("Automated Generation of Sailing Training Videos ⛵🤖")
uploadText = st.subheader(" 👈 Upload your files to get started!!")


# if st.button("Cache Clear"):
#     st.cache_data.clear()


# videoFiles = st.file_uploader( 
#     label="Input your video files here.", 
#     accept_multiple_files=True,
#     type=[".mp4"]
#     )

# gpxFiles = st.file_uploader(
#     label="Input your GPX file here.",
#     accept_multiple_files=False,
#     type=[".gpx"]
#     )

if gpxFiles:
    with st.spinner(text="Processing GPX file..."):
        gpxFrame, gpxDuration = a.gpxDfCreation(gpxFiles)
    trimmedDf = gpxFrame
    gpxSuccess = st.success("GPX file processed succesfully!")
    time.sleep(5)
    gpxSuccess.empty()
    

if videoFiles:
    allUploaded = all(file is not None for file in videoFiles)

    if allUploaded:
        concatProgress = st.progress(0,text="")
        with st.spinner(text="Processing video files..."):
            fullVideo, videoDuration = a.videoConcat(videoFiles, concatProgress)
        trimmedVideo = fullVideo
        videoSuccess= st.success("Video files processed succesfully!")
        time.sleep(5)
        concatProgress.empty()
        videoSuccess.empty()
        # st_folium(finalMap, height=451, width=700)


if allUploaded and gpxFiles:
    uploadText.empty()
    difference, trimDecision = a.timeDifference(videoDuration, gpxDuration)
    print("here")
    if trimDecision == gpxDuration:
        print("GPX Modal")
        gpxModal.open()
        if gpxModal.is_open():
            with gpxModal.container():
                print("in modal container")
                st.write(f"It appears your GPX data is {round(difference)} seconds longer than your video.")
                st.write()
                decision = st.radio("What part of the data would you like to be trimmed?", ("Beggining","End","Both"))
                trimmedDf = a.trim("GPX", decision, difference, frame=gpxFrame)
        else:
            print("Not opening")
    else:
        print("Video Modal")
        videoModal.open()
        if videoModal.is_open():
            with videoModal.container():
                st.write(f"It appears your video is {round(difference)} seconds longer than your GPX data.")
                st.write()
                decision = st.radio("What part of the video would you like to be trimmed?", ("Beggining","End","Both"))
                trimmedVideo = a.trim("Video", decision, difference, fullVideo=fullVideo)
        
    st.sidebar.header("Choose your options")
    manouverType = st.sidebar.radio('Do you want to see tacks or gybes?', ("Tacks","Gybes"))
    windDirection = st.sidebar.selectbox('What was the wind direction during your sail?',("N","NE","E","SE","S","SW","W","NW"))
    numerOfClips = st.sidebar.slider('Number of Clips', 1,8)
    
    if manouverType and windDirection and numerOfClips:
        finalMap, trainingVideo = a.main(trimmedDf, trimmedVideo, manouverType, windDirection, numerOfClips)
        if trainingVideo:
            st.video(trainingVideo)
            st.download_button(label="Click here to download your video!", data=trainingVideo, file_name="sailingTrainingVideo.mp4")

# if binaryDifference:
#     #modal code
#     pass  

    


