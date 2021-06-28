import time
import cv2
import datetime as dt
import os
from RPi import GPIO
from imageai.Detection import ObjectDetection

import setting


class Detecting:
    def __init__(self):
        self.is_detecting=False
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        GPIO.setup(11, GPIO.IN)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(16, GPIO.IN)

    def powerdet(self):
        GPIO.output(7, 1)
        GPIO.output(18, 1)

    def stopdet(self):
        GPIO.output(7, 0)
        GPIO.output(18, 0)

    async def detecting(self, main):
        time.sleep(60)
        print("Czujniki skalibrowane")
        while self.is_detecting:
            j = GPIO.input(11)
            i = GPIO.input(16)
            if (j==0):
                print("Wtrząs: " + str(j) + "\n")
                self.stopdet()
                self.is_detecting = False
                setting.isAlert = True
                if(not main.vid.isRecording):
                    main.capturing_thread()
                    main.vid.record_setting()
                    main.recording_thread()
                main.type = "Wstrząs"
                main.send_notification_thread()
            elif (i==1):
                print("Ruch: " + str(i) + "\n")
                setting.isAlert = True
                GPIO.output(18, 0)
                self.is_detecting = False
                main.capturing_thread()
                main.recording_thread()
                main.type = "Ruch"
                main.object_thread()


    async def object_detecting(self, main):
        time.sleep(5)
        imgname = dt.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
        p = os.path.join("/home/project/images", imgname)
        ret, frame = main.vid.get_frame()
        cv2.imwrite(p, frame)
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(os.path.join("/home/project", "resnet50_coco_best_v2.0.1.h5"))
        self.detector.loadModel()


        detections = self.detector.detectObjectsFromImage(input_image=p,  output_image_path=p+"_det.png")

        for eachObject in detections:
            if(eachObject['name']=='person'):
                main.send_notification_thread(p)
            print(eachObject["name"], " : ", eachObject["percentage_probability"])