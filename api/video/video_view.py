import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect

def camera_stream():
    rtsp_url = "rtsp://adminRLlarena:server2410@192.168.1.69:554/stream1"
    cap = cv2.VideoCapture(rtsp_url)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir el frame a JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)

        # Enviar el frame como respuesta
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imgencode.tobytes() + b'\r\n')

def camera_view(request):
    print("Camera view ejecutada")
    return StreamingHttpResponse(camera_stream(), content_type='multipart/x-mixed-replace; boundary=frame')

