

# import the necessary packages
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from matplotlib import pyplot as plt
from imutils.video import FPS
import os
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-i", "--input_method", required=True,
	help="path to video or use camera")
#ap.add_argument('-w', '--weights', default='mmod_human_face_detector.dat',
 #               help='path to weights file')
args = vars(ap.parse_args())


# initialize dlib's face detector (HOG-based) and then load our
# trained shape predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
#detector = dlib.cnn_face_detection_model_v1(args["weights"])
predictor = dlib.shape_predictor(args["shape_predictor"])

camera_video=int(args["input_method"])
if camera_video is 0:
# initialize the video stream and allow the cammera sensor to warmup
	print("[INFO] camera sensor warming up...")
	vs = cv2.VideoCapture(0) 
	time.sleep(2.0)
	#fps = vs.get(cv2.CAP_PROP_FPS)
elif camera_video is 1:
	vs = cv2.VideoCapture("NTHU_yAWNING/16-FemaleGlasses-Yawning.avi")
	#vs=cv2.VideoCapture("D:/sayus/Pictures/Camera Roll/WIN_20200716_18_36_16_Pro.mp4")
	#fps = vs.get(cv2.CAP_PROP_FPS)
	#fps = FPS().start()
else:
	print("Invalid Argument")

d=0
e=0
feature_extractor=load_model('feature_extractor_1.h5')
yawn_detector=load_model('GRU_best_1.h5')

yawn_detection_sigmoid=0.70
yawn_detection_frames=0
yawn_detection=0
input_feature_extractor=[]
count=0
start_time = time.perf_counter()
is_yawn=False
# loop over the frames from the video stream
while True:
	# grab the frame from the video stream, resize it to have a
	# maximum width of 400 pixels, and convert it to grayscale
	grabbed,frame = vs.read()
	if grabbed==False:
			#vs = cv2.VideoCapture("NTHU_yAWNING/16-FemaleGlasses-Yawning.avi")
			break
			#grabbed,frame = vs.read()
	count=count+1
	frame = imutils.resize(frame, width=400)
	# detect faces in the grayscale frame
	rects = detector(frame, 0)
	# loop over the face detections
	for rect in rects:
		# convert the dlib rectangle into an OpenCV bounding box and
		# draw a bounding box surrounding the face
		# use our custom dlib shape predictor to predict the location
		# of our landmark coordinates, then convert the prediction to
		# an easily parsable NumPy array
		shape = predictor(frame, rect)
		shape = face_utils.shape_to_np(shape)
		(x, y, w, h) = cv2.boundingRect(shape)
		#print("x, y, w , h: ", x, y,w,h)
		#cv2.rectangle(frame, (x, y-int(h)), (x + int(5*w/4), y + int(3*h/2)), (0, 255, 0), 2)
		#cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		#roi = frame[int(y-0.3*h):int(y + 3*h), x:int(x + 1.5*w)]
		roi = frame[y-int(h/3):y + int(h), x:x + int(w)]
		#roi = frame[y:y+h, x:x+w]
		roi=cv2.resize(roi,(50,50))
		cv2.rectangle(frame, (x, y-int(h/3)), (x + int(w), y + int(5*h/4)), (0, 255, 0), 2)
		input_feature_extractor.append(roi)
		#fps.update()
		if len(input_feature_extractor)<32:
			continue
		input_feature_extractor=np.array(input_feature_extractor)
		#print("input_feature_extractor: ",  input_feature_extractor.shape)
		out_feature_extractor=feature_extractor.predict(input_feature_extractor)
		#print("out_feature_extractor: ", out_feature_extractor.shape)
		out_feature_extractor=out_feature_extractor.reshape(1,32,256)
		out_yawn_detector=yawn_detector.predict(out_feature_extractor)
		#print(out_yawn_detector)
		#out_yawn_detector=out_yawn_detector.reshape(32,1)
		print(out_yawn_detector)
		#print()
		#for i in out_yawn_detector:
		#	print(i)
		if out_yawn_detector > yawn_detection_sigmoid:
			yawn_detection=yawn_detection+1
			if yawn_detection>yawn_detection_frames:
				frame = cv2.putText(frame, 'Yawning', (275,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)
				end_time = time.perf_counter()
				u1=float("{:.2f}".format(count/(end_time-start_time)))
				u="fps: "+str(u1)
				cv2.putText(frame, u, (15,25), cv2.FONT_HERSHEY_SIMPLEX ,  
	             		   1, (255,0,0), 1, cv2.LINE_AA)
				cv2.imwrite(os.path.join('NTHU_yAWNING/y_final_yawn1',str(d)+'.jpg'), frame)
				is_yawn=True
				yawn_detection=0
		else:
			yawn_detection=0
		input_feature_extractor=[]
		# show the frame
	end_time = time.perf_counter()
	u1=float("{:.2f}".format(count/(end_time-start_time)))
	u="fps: "+str(u1)

#	u="fps: "+str(fps)
	if is_yawn==False:
		print("maro")
		frame = cv2.putText(frame, 'Not Yawning', (205,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)
	else:
		is_yawn=False
	cv2.putText(frame, u, (15,25), cv2.FONT_HERSHEY_SIMPLEX ,  
	             		   1, (255,0,0), 1, cv2.LINE_AA) 
	print("Reached FPS of: ", count / (end_time - start_time))
	cv2.imshow("Frame", frame)
	cv2.imwrite(os.path.join('NTHU_yAWNING/y_final_not_yawn1',str(d)+'.jpg'), frame)
	d=d+1
	#cv2.imwrite(os.path.join('NTHU_yAWNING/fig_1_2',str(e)+'.jpg'), roi)
	#e=e+1
		#cv2.waitKey(0) #& 0xFF
	if cv2.waitKey(1) & 0xFF == ord('q'):
       		break

cv2.destroyAllWindows()
vs.release()