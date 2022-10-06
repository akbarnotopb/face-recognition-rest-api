import face_recognition as fr
import numpy as np
import os

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

    def extractFeatures(self, file, output="ndarray"):
        if not os.path.exists(file):
            raise Exception("File not found!")
            
        image = fr.load_image_file(file)
        face_locations = fr.face_locations(image, number_of_times_to_upsample=2)
        encoding = fr.face_encodings(image, known_face_locations=face_locations)
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

    