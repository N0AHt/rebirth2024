import cv2 as cv
import numpy as np 
import matplotlib.pyplot as plt


def cv_play(data, window_name = None, scale = 1):

    '''
    display all frames in the array in an interactive plot window from openCV2
    '''

    frameID = 0
    frame = data[frameID].copy()
    h, w = frame.shape[0:2]

    if window_name:
        window_name = window_name
    else:
        window_name = 'Display Tracks   (Press Q to Quit)'

    try:
        #create and rescale window
        cv.namedWindow(window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name, h*scale, w*scale)

        #Frame Trackbar
        def update_frame(x): #callback function for trackbar - default argument is the position of the track bar
            pass
        cv.createTrackbar('Frame',window_name,0,len(data)-1,update_frame)

    except Exception as e:
        print(e)


    while True:

        try:
            # Process and display a Frame
            frameID = cv.getTrackbarPos('Frame',window_name)
            frame = data[frameID]
            
            #process frame here
            frame = cv.normalize(frame, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U) # convert from uint16 to uint8 for display with openCV
            # frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)

            cv.imshow(window_name, frame)


            # Handle key events for navigation
            key = cv.waitKey(5)
            if key == ord('a'):  # Move to the previous frame
                frameID = max(frameID - 1, 0)
                cv.setTrackbarPos('Frame', window_name, frameID)

            elif key == ord('d'):  # Move to the next frame
                frameID = min(frameID + 1, len(data) - 1)
                cv.setTrackbarPos('Frame', window_name, frameID)

            elif key == ord('q'):  # Quit
                cv.destroyAllWindows()
                break

        except Exception as e:
            print(e)
            cv.destroyAllWindows()
            break
        
    cv.destroyAllWindows()