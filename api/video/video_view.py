from django.db.models import Q
from api.models import Reservacion, ConteoPersonas
from datetime import datetime, time, timedelta
from django.core.files import File
import cv2
import mediapipe as mp
import numpy as np
from django.http import HttpResponse, StreamingHttpResponse
import os
import time


BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode


model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/efficientdet_lite0.tflite')
options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    max_results=10,  # Aumentar el número máximo de resultados
    running_mode=VisionRunningMode.IMAGE)
detector = ObjectDetector.create_from_options(options)

def conteo(request):
    now = datetime.now()
    reservacion = Reservacion.objects.filter(
        fecha=now.date(),
        hora_inicio__lte=now.time(),
        hora_final__gte=now.time()
    ).first()

    if not reservacion:
        return HttpResponse("No hay reservaciones en curso")

    start_time = reservacion.hora_inicio.strftime("%H:%M")
    end_time = reservacion.hora_final.strftime("%H:%M")

    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    rtsp_url = "rtsp://adminRLlarena:server2410@192.168.1.84 :554/stream1"

    while datetime.now().strftime("%H:%M") < end_time:
        if datetime.now().strftime("%H:%M") >= start_time:
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                return HttpResponse("No se pudo abrir el stream RTSP")

            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
                photo_path = os.path.join(temp_dir, filename)
                cv2.imwrite(photo_path, frame)

                # Conteo de personas...
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = detector.detect(mp_image)

                person_count = 0
                for detection in detection_result.detections:
                    for category in detection.categories:
                        if category.category_name == 'person' and category.score > 0.3:
                            person_count += 1

                txt_path = photo_path.replace(".jpg", ".txt")
                with open(txt_path, "w") as f:
                    f.write(str(person_count))

            cap.release()
            time.sleep(60)

    photos = os.listdir(temp_dir)
    max_person_count = 0
    best_photo = None
    best_photo_txt = None

    for photo in photos:
        if photo.endswith(".txt"):
            with open(os.path.join(temp_dir, photo), "r") as f:
                count = int(f.read())
                if count > max_person_count:
                    max_person_count = count
                    best_photo_txt = photo
                    best_photo = photo.replace(".txt", ".jpg")

    if best_photo and best_photo_txt:
        final_photo_path = os.path.join(temp_dir, best_photo)
        with open(final_photo_path, 'rb') as img_file:
            ConteoPersonas.objects.create(
                reservacion=reservacion,
                foto=File(img_file, name=best_photo),
                personas_contadas=max_person_count,
                fecha=datetime.now().date()
            )

        for photo in photos:
            os.remove(os.path.join(temp_dir, photo))

        return HttpResponse(f"La mejor foto fue guardada en la base de datos con {max_person_count} personas")
    else:
        for photo in photos:
            os.remove(os.path.join(temp_dir, photo))
        return HttpResponse("No se encontró ninguna foto con conteo de personas")