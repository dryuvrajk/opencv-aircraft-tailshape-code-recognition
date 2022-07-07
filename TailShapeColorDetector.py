import numpy as np
import cv2 as cv

# Defining some global values
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
BLUE = (255, 0, 0)

TRIANGLE = 3
RECTANGLE = 4

# Defining the lower and upper limits for the 3 colors upon calibration
LOWER_RED1 = np.array([0,100,120])
UPPER_RED1 = np.array([10,255,255])
LOWER_RED2 = np.array([170,100,120])
UPPER_RED2 = np.array([180,255,255])
LOWER_YELLOW = np.array([20,80,100])
UPPER_YELLOW = np.array([40,255,255])
LOWER_BLUE = np.array([80,80,40])
UPPER_BLUE = np.array([125,255,255])

# Function to draw the result on the lower right corner of an image
def drawResult(color, shape, img):
    corners = np.array([])
    height, width, _ = img.shape
    text = '';
    if shape == TRIANGLE:
        corners = np.array([[width - 45, height - 70],
                            [width - 20, height - 20],
                            [width - 70, height - 20]])
        if color == RED:
            text = 'A'
        elif color == YELLOW:
            text = 'B'
        elif color == BLUE:
            text = 'C'
    elif shape == RECTANGLE:
        corners = np.array([[width - 70, height - 70],
                            [width - 70, height - 20],
                            [width - 20, height - 20],
                            [width - 20, height - 70]])
        if color == RED:
            text = 'D'
        elif color == YELLOW:
            text = 'E'
        elif color == BLUE:
            text = 'F'
    if shape == TRIANGLE or shape == RECTANGLE:
        cv.fillPoly(img, [corners], color)
        cv.putText(img, text, (width - 120, height - 24), cv.FONT_HERSHEY_DUPLEX, 2, color, 2, cv.LINE_AA)
    return img

# Function to find any contour and count its corners
def getCorners(mask, img):
    _, contours, _ = cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE + 2)
    n = len(contours)
    ret = 0
    for i in range(0,len(contours)):
        cnt = contours[i]
        epsilon = 0.03 * cv.arcLength(cnt, True)
        approx = cv.approxPolyDP(cnt, epsilon, True)
        cv.drawContours(img, [approx], 0, YELLOW, -1)
        for corner in approx:
            x, y = corner.ravel()
            cv.circle(img, (x, y), 3, BLUE, -1)
        ret = max(ret, len(approx))
    return ret, img

'''
palette = cv.imread('color_wheel.png')
palette2 = cv.imread('HSV.png')
red_rectangle = cv.imread('red_rectangle.png')
red_triangle = cv.imread('red_triangle.png')
yellow_rectangle = cv.imread('yellow_rectangle.png')
yellow_triangle = cv.imread('yellow_triangle.png')
blue_rectangle = cv.imread('blue_rectangle.png')
blue_triangle = cv.imread('blue_triangle.png')
'''

# Capturing the video feed
WEB_CAM = 0
AV_TO_USB = 1
vid = cv.VideoCapture(WEB_CAM)

while True:
    _, frame = vid.read()

    # Overriding frame by a fixed image for debugging
    '''
    frame = red_triangle
    frame = yellow_triangle
    frame = blue_triangle
    frame = red_rectangle
    frame = yellow_rectangle
    frame = blue_rectangle
    frame = palette2
    '''

    # Blurring the frame to be ready for color filtering and edge detection
    original = frame
    frame = cv.GaussianBlur(frame, (25, 25), 2)
    frame = cv.dilate(frame, np.ones((15, 15), np.uint8))
    frame = cv.erode(frame, np.ones((15, 15), np.uint8))

    # Converting the colors from RGB to HSV
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Generating a binary mask for the 3 colors
    mask_red1 = cv.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask_red2 = cv.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask_red = cv.bitwise_or(mask_red1, mask_red2)
    
    mask_yellow = cv.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
    
    mask_blue = cv.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    # Filtering colors
    red_filter = cv.bitwise_and(frame, frame, mask = mask_red)
    yellow_filter = cv.bitwise_and(frame, frame, mask = mask_yellow)
    blue_filter = cv.bitwise_and(frame, frame, mask = mask_blue)

    # Defining contours and count the corners of each contour
    red_corners, red_contours = getCorners(mask_red, red_filter.copy())
    yellow_corners, yellow_contours = getCorners(mask_yellow, yellow_filter.copy())
    blue_corners, blue_contours = getCorners(mask_blue, blue_filter.copy())

    # Printing the number of corners in each color contour for debugging
    ryb = str(red_corners) + ' ' + str(yellow_corners) + ' ' + str(blue_corners)
    print(ryb)

    # Drawing the result on the original image
    if red_corners >= 3:
        original = drawResult(RED, red_corners, original.copy())
    if yellow_corners >= 3:
        original = drawResult(YELLOW, yellow_corners, original.copy())
    if blue_corners >= 3:
        original = drawResult(BLUE, blue_corners, original.copy())

    # Showing the original image after drawing the result on it
    cv.imshow('Original', original)

    # Showing the used masks and filters for debugging
    #cv.imshow('Red Mask', mask_red)
    #cv.imshow('Red Filter', red_filter)
    #cv.imshow('Red Contours', red_contours)
    
    #cv.imshow('Yellow Mask', mask_yellow)
    #cv.imshow('Yellow Filter', yellow_filter)
    #cv.imshow('Yellow Contours', yellow_contours)
    
    #cv.imshow('Blue Mask', mask_blue)
    #cv.imshow('Blue Filter', blue_filter)
    #cv.imshow('Blue Contours', blue_contours)

    # Breaks out of the loop in case of hitting button 'Q'
    if cv.waitKey(1) & 0xff == ord('q'):
        break

vid.release()
cv.destroyAllWindows()
