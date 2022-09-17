import face_recognition as fr
import numpy as np

class FaceDetector:
    def __init__(self):
        pass

    def compareEmbedding(self, source, target, sourcetype="ndarray" , tolerance = 0.5):
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
        image = fr.load_image_file(file)
        encoding = fr.face_encodings(image)
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

    