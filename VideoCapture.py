import cv2
import time
import datetime as dt
import os

import setting


class VideoCapture:
    def __init__(self, video_source=0):
        self.ret = None
        self.rec_time = 0
        self.isRecording = False
        self.isCapturing = True
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        self.setting = setting.CommandLineParser()
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)


        # create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            'mp4': cv2.VideoWriter_fourcc(*'avc1'),
        }

        self.fourcc = VIDEO_TYPE[self.setting.get_video()['type']]

        # 2. Video Dimension
        STD_DIMENSIONS = {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080)
        }
        self.res = STD_DIMENSIONS[self.setting.get_video()['res']]


        # set video sourec width and height
        self.vid.set(3, self.res[0])
        self.vid.set(4, self.res[1])

        # Get video source width and height
        self.width, self.height = self.res

    async def set_frame(self):
        while self.isCapturing:
            if self.vid.isOpened():
                self.ret, self.frame = self.vid.read()

    def record_setting(self):
        self.time_start = time.time()
        self.filename = dt.datetime.now().strftime('%Y%m%d%H%M%S') + '.' + self.setting.get_video()['type']

        if(setting.isAlert):
            self.path = os.path.sep.join(("/home/project/video", self.filename))
        else:
            self.path = os.path.sep.join(("/home/project/", self.filename))

        self.out = cv2.VideoWriter(self.path,
                                   self.fourcc,
                                   int(self.setting.get_video()['frame']),
                                   self.res)
        self.frame_time = float(1/int(self.setting.get_video()['frame']))
        print(self.frame_time)

    async def recording(self, main):
        while self.isRecording:
            frametime = time.time()
            if self.ret:
                # Return a boolean success flag and the current frame converted to BGR
                self.rec_time = int(time.time() - self.time_start)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(self.frame,
                            dt.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                            (int(self.width/4), self.height - int(self.height/144)),
                            font, self.height/360,
                            (255, 255, 0),
                            1,
                            cv2.LINE_4)
                if main.obd.is_obd:
                    cv2.putText(self.frame,
                                str(main.obd_value_speed),
                                (0, self.height - int(self.height/144)),
                                font, self.height/720,
                                (255, 255, 0),
                                1,
                                cv2.LINE_AA)
                self.out.write(cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
            if (time.time()- self.time_start >= 60*int(self.setting.get_video()['time'])):
                if(setting.isAlert):
                    self.isRecording = False
                    self.isCapturing = False
                    setting.isAlert = False
                    main.detecting_thread()
                    main.send_video_thread(self.path)
                else:
                    self.record_setting()
            if time.time()-frametime<self.frame_time:
                time.sleep(self.frame_time-(time.time()-frametime))

    def get_recTime(self):
        return self.rec_time

    # To get frames
    def get_frame(self):
        if self.ret:
            # Return a boolean success flag and the current frame converted to BGR
            return (self.ret, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        else:
            return (self.ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()