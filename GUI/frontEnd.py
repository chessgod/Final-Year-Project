import streamlit as st
from streamlit_folium import st_folium
from app import main
import moviepy;

# Upload file #
st.sidebar.header('Upload your files here!')
videoFiles = st.sidebar.file_uploader("Video Files here", type=['mov', 'mp4'], accept_multiple_files=True)

st.sidebar.header('Upload GPX files here!')
gpxFiles = st.sidebar.file_uploader("GPX files here", type=['gpx'])

st.title("Automated Generation of Sailing Training Videos")

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

if videoFiles and gpxFiles:

    allUploaded = all(file is not None for file in videoFiles)

    if allUploaded:
        st.sidebar.header("Choose your options")
        manouverType = st.sidebar.radio('Do you want to see tacks or gybes?', ("Tacks","Gybes"))
        numerOfClips = st.sidebar.slider('Number of Clips', 1,8)
        finalMap, trainingVideo = main(gpxFiles,videoFiles)
        st_folium(finalMap, height=451, width=700)

    
    if trainingVideo:
        st.video(trainingVideo)
        st.download_button(label="Click here to download your video!", data=trainingVideo, file_name="sailingTrainingVideo.mp4")

    
else:

    st.subheader(" 👈 Upload your files to get started!!")
    # print("Video Files:", videoFiles)

    # do something
    # print(type(gpxFiles))
    # print(type(videoFiles[0]))


    


