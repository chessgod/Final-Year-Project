import streamlit as st
from streamlit_folium import st_folium
import app as a
import moviepy;
import time;
import pandas as pd;
from streamlit_modal import Modal;
import streamlit.components.v1 as components

@st.cache_data()
def processGPX(files):
    with st.spinner(text="Processing GPX file..."):
        gpxFrame, gpxDuration = a.gpxDfCreation(files)
    trimmedDf = gpxFrame
    gpxSuccess = st.success("GPX file processed succesfully!")
    gpxSuccess.empty()
    return trimmedDf, gpxDuration

@st.cache_resource()
def processVideo(files):
    concatProgress = st.progress(0,text="")
    with st.spinner(text="Processing video files..."):
        fullVideo, videoDuration = a.videoConcat(files, concatProgress)
    concatProgress.empty()
    return fullVideo, videoDuration

allUploaded = False
videoModal = Modal(title="Video Modal",key="1")
gpxModal = Modal(title= "GPX Modal",key="2")
# Upload file #
st.sidebar.header('Upload GPX files here!')
gpxFiles = st.sidebar.file_uploader("GPX files here", type=['gpx'])

st.sidebar.header('Upload your Video files here!')
videoFiles = st.sidebar.file_uploader("Video Files here", type=['mov', 'mp4'], accept_multiple_files=True)


st.title("Automated Generation of Sailing Training Videos ⛵🤖")
uploadText = st.subheader(" 👈 Upload your files to get started!!")


if gpxFiles:
    trimmedDf, gpxDuration = processGPX(gpxFiles)


if videoFiles:
    allUploaded = all(file is not None for file in videoFiles)
    if allUploaded:
        fullVideo, videoDuration = processVideo(videoFiles)
        trimmedVideo = fullVideo

if allUploaded and gpxFiles:
    uploadText.empty()
    difference, trimDecision = a.timeDifference(videoDuration, gpxDuration)
    if trimDecision == gpxDuration:
        with gpxModal.container():
            with st.form("gpxModal"):
                # html_string = '''
                #     <script language="javascript">
                #         document.querySelector("body").style.backgroundcolor = rgb(14, 17, 23);
                #     </script>
                #     '''
                # components.html(html_string)
                st.markdown(f"It appears your GPX data is {round(difference)} seconds longer than your video.",)
                st.write()
                decision = st.radio("What part of the data would you like to be trimmed?", ("Beggining","End","Both"))
                submitDecision = st.form_submit_button(label="Submit")
                if submitDecision:
                    gpxModal.close()
                    trimmedDf = a.trim("GPX", decision, difference, frame=trimmedDf)
                    
            
    else:
        with videoModal.container():
            st.write(f"It appears your video is {round(difference)} seconds longer than your GPX data.")
            st.write()
            decision = st.radio("What part of the video would you like to be trimmed?", ("Beggining","End","Both"))
            submitDecision = st.button(label="Submit")
            if submitDecision:
                trimmedVideo = a.trim("Video", decision, difference, fullVideo=fullVideo)
        
    st.sidebar.header("Choose your options")
    with st.sidebar.form(key="userOptions"):
        manouverType = st.sidebar.radio('Do you want to see tacks or gybes?', ("Tacks","Gybes"))
        windDirection = st.sidebar.selectbox('What was the wind direction during your sail?',("N","NE","E","SE","S","SW","W","NW"))
        numerOfClips = st.sidebar.slider('Number of Clips', 1,8)
        userOptionsSubmit = st.sidebar.form_submit_button(label="Submit")
  
    if userOptionsSubmit:
        finalMap, trainingVideo = a.main(trimmedDf, trimmedVideo, manouverType, windDirection, numerOfClips)
        if trainingVideo:
            st.video(trainingVideo)
            st.download_button(label="Click here to download your video!", data=trainingVideo, file_name="sailingTrainingVideo.mp4")

 
