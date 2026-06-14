import cv2
#IMG_4235 à 4249

def nothing(x):
    pass

img = cv2.imread("IMG_4243.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.namedWindow("Trackbars")

cv2.createTrackbar("Hmin", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("Hmax", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("Smin", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Smax", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("Vmin", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Vmax", "Trackbars", 255, 255, nothing)

while True:
    hmin = cv2.getTrackbarPos("Hmin", "Trackbars")
    hmax = cv2.getTrackbarPos("Hmax", "Trackbars")
    smin = cv2.getTrackbarPos("Smin", "Trackbars")
    smax = cv2.getTrackbarPos("Smax", "Trackbars")
    vmin = cv2.getTrackbarPos("Vmin", "Trackbars")
    vmax = cv2.getTrackbarPos("Vmax", "Trackbars")

    lower = (hmin, smin, vmin)
    upper = (hmax, smax, vmax)

    mask = cv2.inRange(hsv, lower, upper)

    cv2.imshow("Image", img)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Détruit les fenêtres théoriquement
cv2.destroyAllWindows()

# Astuce indispensable pour Mac : force le vidage de la pile d'événements
for i in range(5):
    cv2.waitKey(1)