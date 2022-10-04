import cv2
import numpy as np
import pytesseract
cap = cv2.VideoCapture(0)
cap.set(3, 300)
cap.set(4, 400)
counter = 0
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
y = 120
x = 15
h = 20
w = 340
while True:
    ret, frame = cap.read()
    #cv2.putText(frame, "Focus CC number below", (50,150), cv2.FONT_HERSHEY_COMPLEX, .6, (0,255,0), 2)
    #rect = cv2.rectangle(img=frame, pt1=(20,190), pt2=(300,220), color=(0,255,0), thickness=3)
    cv2.imshow("default frame", frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray frame", gray)
    blur = cv2.GaussianBlur(frame, (5,5), cv2.BORDER_DEFAULT)
    cv2.imshow("blur", blur)
    canny = cv2.Canny(frame, 125, 255)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap = np.uint8(np.abs(lap))
    cv2.imshow("laplacian", lap)
    sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    cv2.imshow("sobel", sobel)
    cv2.imshow("canny", canny)
    ret1, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    cv2.imshow("threshold", thresh)
    ret1, thresh_inv = cv2.threshold(canny, 100, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("threshold inverse", thresh_inv)
    crop_img = thresh_inv[y:y+h, x:x+w]
    cv2.imshow("crop image", crop_img)
    
    
    if cv2.waitKey(1) & 0xFF==ord("c"):
        counter+=1
        for i in range(counter):
            cv2.imwrite(f"new picture{i}.jpg", frame)
        #print(pytesseract.image_to_string(thresh_inv))
    
    if cv2.waitKey(1) & 0xFF==ord("q"):
        break

cap.release()
cv2.destroyAllWindows()