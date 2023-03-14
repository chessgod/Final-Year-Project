import cv2
import moviepy.editor as mp

def getVidData(videoFile):
    capture = cv2.VideoCapture(videoFile)
    # height, width = capture.shape
    # newHeight = height * numVideos
    # newWidth = width * numVideos
    if(capture.isOpened() == 'False'):
        print("It ain't gonna open boss.")
    while(capture.isOpened()):
        ret, frame = capture.read()
        if(ret==True):
            cv2.imshow('frame', frame)

            if(cv2.waitKey(25) == ord('q')):
               break
        else:
            break   
    capture.release()
    cv2.destroyAllWindows()

def splitVideo(original, tacks, gybes):
    validDecision = False
    while validDecision == False:
        print("Would you like to see tacks or gybes? (t) , (g)")
        decision = input()
        if(decision == "t" or decision == "g"):
            validDecision = True
            
    print("How many videos would you like to see?")
    numVideos = input()
    fullVid = mp.VideoFileClip(original)
    duration = fullVid.duration()
    for x in range(int(numVideos)):
        
    example1 = mp.VideoFileClip(original).subclip(0, 10)
    example2 = mp.VideoFileClip(original).subclip(10, 20)
    example3 = mp.VideoFileClip(original).subclip(20, 30)

    all = mp.clips_array([[example1, example2, example3]])

    all.write_videofile("testing.mp4", logger =None, verbose = False)

    # getVidData("testing.mp4")


def vidStart(video):
    pass