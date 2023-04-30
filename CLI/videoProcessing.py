import moviepy.editor as mp
import timeit
import tempfile

# Function for concatenating clips
def combineClips(files, progressBar=None):
    formattedArray = []
    if(files == None):
        print("Please input all the clips. (filepaths separated by one space each)")
        userInput = input()
        clipArray = userInput.split(" ")
        #Taking the inputted string and turning it into a VideoClip with moviepy
        formattedArray = [mp.VideoFileClip(clip) for clip in clipArray]

    else:
        for i, clip in enumerate(files):
            # file_bytes = clip.read()
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file.write(clip.read())
            video = mp.VideoFileClip(tmp_file.name)
            formattedArray.append(video)

            if progressBar:
                progressBar.progress((i+1) / len(files),text=f"Video number {i} sucessfully processed...")

    #Concatenating all inputted videos into one
    finalVideo = mp.concatenate_videoclips(formattedArray)
    return finalVideo, finalVideo.duration

# Function for trimming the video if it is longer than GPX
def videoTrim(video, decision, offset):
    # Code for calculating offset in relation to the end of the video
    endOffset = video.end - offset
    # Cutting the video dependant on end or beggining decision
    if(decision == "e"):
        video = video.cutout(endOffset, video.end)
    elif(decision == "b"):
        video = video.cutout(0, offset)
    return video

# Fucntion for splitting the video into turns, and outputting it
def splitVideo(original, frame, manouver=None, numVideos=None):
    validDecision = False # Used for input validation
    clipList = [] #Will store clips of turns
    tacksFrame = frame[frame['manouverType'].isin(["TS","TP"])].copy() # DataFrame with just tacks
    gybesFrame = frame[frame['manouverType'].isin(["GS","GP"])].copy() # DataFrame with just gybes

    # Getting start time of video
    # print("HEAD OF FRAME", frame.head)
    startTime = frame["time"].iloc[0]
    # Converting to seconds
    startTime = int(startTime.timestamp())

    # Input validation from user
    if manouver == None:
        while validDecision == False:
            print("Would you like to see tacks or gybes? (Tacks) , (Gybes)")
            manouver = input()
            if(manouver == "Tacks" or manouver == "Gybes"):
                validDecision = True
                break
            print("That is not a valid input.")

        print("How many videos would you like to see?")
        numVideos = input()

    # If statement on wether the user wants to see tacks or gybes
    # As you can see not very optimised code, a lot of repeated lines
    if(manouver == "Tacks"):
        # Taking a random number of turns dependant on how many the user wants to see
        sampleFrame = tacksFrame.sample(n=int(numVideos))
        # Iterating through sampleFrame
        for index, x in sampleFrame.iterrows():
            tempTime = x["time"]
            tempTime = int(tempTime.timestamp())
            # Calculating start and end time of video
            start = tempTime - startTime
            end = start + 20 # for now the clip time has been set to 20 seconds, it can be edited her
                             # in future I wnt the "slider" system where the user can choose how long they want the clips to be
            # Stores clip into temp variable 
            temp = original.subclip(start, end)
            clipList.append(temp)
    else:
        # Taking a random number of turns dependant on how many the user wants to see
        sampleFrame = gybesFrame.sample(n=int(numVideos))
        for index, x in sampleFrame.iterrows():
            tempTime = x["time"]
            tempTime = int(tempTime.timestamp())
            start = tempTime - startTime
            end = start + 20
            temp = original.subclip(start, end)
            clipList.append(temp)

    # Creates a moviepy clips_array, which is what will be rendered
    all = mp.clips_array([clipList])

    all.write_videofile("static/files/final.mp4", audio=False)

    # Rendering of the vieo, this takes quite a while and no matter what I do it does not get faster :(
    # all.write_videofile("testing.mp4", audio=False, threads=300, fps=30, preset="ultrafast", codec="libx264")

    return all
    # all.write_gif("testing.gif")
