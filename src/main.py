import falcon,json
from facedetector.facedetector import FaceDetector
from falcon_multipart.middleware import MultipartMiddleware
import hashlib

SECRET_KEY = ""
with open(".env") as env:
    _str = env.readlines()
    for s in _str:
        s = s[:-1] #remove \n
        res = s.split("=")
        if(res[0] == "SECRET_KEY"):
            SECRET_KEY = res[1]

MODEL = FaceDetector()

class RegisterFaces:
    def on_post(self, req, res):
        token = req.get_param("token")
        sha = req.get_param("sha")

        if(sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest()):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_files = req.get_param_as_list("faces")
        features = []
        for incoming_file in incoming_files:
            try:
                features.append(MODEL.extractFeatures(incoming_file.file,  output="list"))
            except:
                features.append("")
        
        res.status = falcon.HTTP_200
        res.text = json.dumps(features)

class RegisterFace:
    def on_post(self, req, res):
        token = req.get_param("token")
        sha = req.get_param("sha")

        if(sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest()):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_file = req.get_param("face")
        try:
            features = MODEL.extractFeatures(incoming_file.file, output="list")
        except Exception as e:
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":str(e)})
            return 

        res.status = falcon.HTTP_200
        res.text = json.dumps(features)



class VerifyFace:
    def on_post(self, req, res):
        token = req.get_param("token")
        sha = req.get_param("sha")

        if(sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest()):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_file = req.get_param("face")
        sourcetype = req.get_param("sourcetype")
        list_of_features = req.get_param_as_list("encodings") if sourcetype == "string" else json.loads(req.get_param("encodings"))
        tolerance = req.get_param("tolerance")

        if(tolerance != None):
            tolerance = float(tolerance)

        features = None
        extracted = False
        try:
            features = MODEL.extractFeatures(incoming_file.file)
            extracted = True
        except Exception as e:
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":str(e)})
            return 
        
        if not extracted:
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":"Something went wrong!"})
            return 
        
        verification_result = MODEL.compareEmbedding(list_of_features, features, sourcetype=sourcetype, tolerance = tolerance if tolerance != None else 0.5) 

        res.text = json.dumps(verification_result, default=str)


class ServerStatus:
    def on_get(self, req, res):
        res.status = falcon.HTTP_200
        res.text = json.dumps({"message":"running normal"})


app = falcon.App(cors_enable = True,middleware=[MultipartMiddleware()])


def generic_error_handler(ex, req, resp, params):
    raise falcon.HTTPInternalServerError(title="500 Internal Server Error", description=str(ex)) 

app.add_error_handler(Exception, generic_error_handler)

app.add_route("/register", RegisterFaces())
app.add_route("/register-single", RegisterFace())
app.add_route("/verify", VerifyFace())
app.add_route("/status", ServerStatus())