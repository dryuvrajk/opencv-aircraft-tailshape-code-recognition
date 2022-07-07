import numpy as np
import cv2
import pytesseract

# Defining some global values
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
BLUE = (255, 0, 0)

TRIANGLE = 3
RECTANGLE = 4

# Defining the lower and upper limits for the black color
LOWER_BLACK = np.array([0,0,0])
UPPER_BLACK = np.array([140,120,120])

# Function to draw the result on the lower right corner of an image
def drawResult(color, shape, img, text):
    corners = np.array([])
    height, width, _ = img.shape
    if shape == TRIANGLE:
        corners = np.array([[width - 45, height - 70],
                            [width - 20, height - 20],
                            [width - 70, height - 20]])
    elif shape == RECTANGLE:
        corners = np.array([[width - 70, height - 70],
                            [width - 70, height - 20],
                            [width - 20, height - 20],
                            [width - 20, height - 70]])
    cv2.fillPoly(img, [corners], color)
    cv2.putText(img, text, (width - 120, height - 24),
                cv2.FONT_HERSHEY_DUPLEX, 2, color, 2, cv2.LINE_AA)
    return img

# Capturing the video feed
WEB_CAM = 0
AV_TO_USB = 1
vid = cv2.VideoCapture(AV_TO_USB)

counter = 0
while True:
    _, frame = vid.read()

    alpha, beta = 2, 0
    contrast = cv2.addWeighted(frame, alpha, np.zeros(frame.shape, frame.dtype), 0, beta)

    # Generating a binary mask for the black color
    noisy_mask = contrast[250:,200:440]
    noisy_mask = cv2.inRange(noisy_mask, LOWER_BLACK, UPPER_BLACK)
    mask = noisy_mask.copy()
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    counter %= 80
    if counter == 0:
        text = pytesseract.image_to_string(mask, lang = 'antonio')
    counter += 1

    print(text)
    
    # Checking if the text is similar to a Tail ID Number
    if text == 'UH8':
        frame = drawResult(RED, TRIANGLE, frame.copy(), 'A')
    elif text == 'L6R':
        frame = drawResult(YELLOW, TRIANGLE, frame.copy(), 'B')
    elif text == 'G7C':
        frame = drawResult(BLUE, TRIANGLE, frame.copy(), 'C')
    elif text == 'S1P':
        frame = drawResult(RED, RECTANGLE, frame.copy(), 'D')
    elif text == 'JW3':
        frame = drawResult(YELLOW, RECTANGLE, frame.copy(), 'E')
    elif text == 'A2X':
        frame = drawResult(BLUE, RECTANGLE, frame.copy(), 'F')
        
    # Showing the original image after drawing the result on it
    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)

    # Breaks out of the loop in case of hitting button 'q'
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()
