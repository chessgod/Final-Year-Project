import cv2
import moviepy.editor as mp
import timeit

# def getVidData(videoFile):

#     capture = cv2.VideoCapture(videoFile)

#     duration = capture.get(cv2.CAP_PROP_POS_MSEC)

#     print("Video Duration: " ,duration)


    
    # # height, width = capture.shape
    # # newHeight = height * numVideos
    # # newWidth = width * numVideos
    # if(capture.isOpened() == 'False'):
    #     print("It ain't gonna open boss.")
    # while(capture.isOpened()):
    #     ret, frame = capture.read()
    #     if(ret==True):
    #         cv2.imshow('frame', frame)

    #         if(cv2.waitKey(25) == ord('q')):
    #            break
    #     else:
    #         break   
    # capture.release()
    # cv2.destroyAllWindows()

def combineClips():
    print("Please input all the clips. (filepaths separated by one space each)")
    userInput = input()
    clipArray = userInput.split(" ")

    formattedArray = [mp.VideoFileClip(clip) for clip in clipArray]

    finalVideo = mp.concatenate_videoclips(formattedArray)

    return finalVideo, finalVideo.duration

def splitVideo(original):
    validDecision = False
    clipList = []
    while validDecision == False:
        print("Would you like to see tacks or gybes? (t) , (g)")
        decision = input()
        if(decision == "t" or decision == "g"):
            validDecision = True
            break
        print("That is not a valid input.")

    print("How many videos would you like to see?")
    numVideos = input()
    fullVid = mp.VideoFileClip(original)
    duration = fullVid.duration
    nextVal = 0
    for x in range(1, int(numVideos)+1):
        temp = mp.VideoFileClip(original).subclip(nextVal, x*10)
        nextVal = x*10
        clipList.append(temp)

    all = mp.clips_array([clipList])

    all.write_videofile("testing.mp4", logger =None, verbose = False)

    # getVidData("testing.mp4")


def vidStart(video):
    pass