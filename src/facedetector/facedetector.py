import face_recognition as fr
import numpy as np
import os
import logging
import imutils
import cv2

logging.basicConfig(
    format='%(asctime)-15s: %(name)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger('connectors-deploy')
LOGGER.setLevel(logging.INFO)

class FaceDetector:
    def __init__(self):
        pass

    def compareEmbedding(self, source, target, sourcetype="ndarray" , tolerance = 0.4):
        databases = []
        for encoded in source:
            if(sourcetype == "string"):
                databases.append(self.string2ndArray(encoded))
            elif(sourcetype == "list"):
                databases.append(np.array(encoded))
            else:
                databases.append(encoded)

        res = fr.compare_faces(databases, target, tolerance=tolerance)
        return res

    def extractFeatures(self, file, output="ndarray" , mode = "fr" ):
        if not os.path.exists(file):
            raise Exception("File not found!")

        if(mode == "fr"):
            image = fr.load_image_file(file, mode="L")
            encoding = fr.face_encodings(image)
        elif(mode == "native"):
            LOGGER.info("native")
            image = cv2.imread(file)
            image = imutils.resize(image, width=600)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            locations = fr.face_locations(rgb)
            LOGGER.info("locations {}".format(locations))
            encoding = fr.face_encodings(image, known_face_locations=locations)
            LOGGER.info("encodings {}".format(encoding))

        if(len(encoding) == 0 ):
            raise Exception("Wajah tidak terdeteksi!")
        elif(len(encoding) > 1):
            raise Exception("Terdapat 2 wajah terdeteksi!")
        
        if output == "string":
            return self.ndArray2String(encoding[0])
        elif output == "list":
            return encoding[0].tolist()
        else:
            return encoding[0]

    def getFaceCount(self, file):
        pass

    def ndArray2String(self, ndarray):
        return np.array2string(ndarray)
    
    def string2ndArray(self, string):
        return np.fromstring(string)

    