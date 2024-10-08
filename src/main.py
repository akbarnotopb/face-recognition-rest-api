import falcon,json
from facedetector.facedetector import FaceDetector
from falcon_multipart.middleware import MultipartMiddleware
import hashlib
from datetime import datetime
import os
import logging, traceback

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(filename='.error_log.log', level=logging.ERROR, filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s')
DEBUG = False
SECRET_KEY = ""
with open(".env") as env:
    _str = env.readlines()
    for s in _str:
        s = s[:-1] #remove \n
        res = s.split("=")
        if(res[0] == "SECRET_KEY"):
            SECRET_KEY = res[1]
        elif res[0] == "PRODUCTION":
            DEBUG = not bool(res[1])

MODEL = FaceDetector()
if(DEBUG):
    logging.warning("Running in debug mode!")

class RegisterFaces:
    def on_post(self, req, res):
        logging.info("Register faces requested...")
        token = req.get_param("token")
        sha = req.get_param("sha")
        mode = req.get_param("mode")

        if(not DEBUG and (token == None or sha == None or sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest())):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_files = req.get_param_as_list("faces")
        features = []
        for incoming_file in incoming_files:
            try:
                file_path = "{}/img/register/{}-{}".format( os.getcwd() ,datetime.now().strftime("%Y%m%d-%H:%M:%S-%f"), incoming_file.filename)
                with open(file_path, "wb") as f:
                    f.write(incoming_file.file.read())
                features.append(MODEL.extractFeatures(file_path,  output="list", mode="native" if mode == None else mode))
            except Exception as e:
                res.status = falcon.HTTP_422
                res.text = json.dumps({"message":str(e)})
                return 
        
        res.status = falcon.HTTP_200
        res.text = json.dumps(features)

class RegisterFace:
    def on_post(self, req, res):
        logging.info("Register face requested...")
        token = req.get_param("token")
        sha = req.get_param("sha")
        mode = req.get_param("mode")


        if(not DEBUG and (token == None or sha == None or sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest())):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_file = req.get_param("face")
        try:
            file_path = "{}/img/register/{}-{}".format( os.getcwd() ,datetime.now().strftime("%Y%m%d-%H:%M:%S-%f"), incoming_file.filename)
            with open(file_path, "wb") as f:
                f.write(incoming_file.file.read())
            features = MODEL.extractFeatures(file_path, output="list", mode="native" if mode == None else mode)
        except Exception as e:
            logging.error(str(e))
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":str(e)})
            return 

        res.status = falcon.HTTP_200
        res.text = json.dumps(features)



class VerifyFace:
    def on_post(self, req, res):
        logging.info("Verify face requested...")
        token = req.get_param("token")
        sha = req.get_param("sha")
        mode = req.get_param("mode")

        if(not DEBUG and (token == None or sha == None or sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest())):
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
            file_path = "{}/img/verify/{}-{}".format( os.getcwd() ,datetime.now().strftime("%Y%m%d-%H:%M:%S-%f"), incoming_file.filename)
            with open(file_path, "wb") as f:
                f.write(incoming_file.file.read())
            features = MODEL.extractFeatures(file_path, mode="native" if mode == None else mode)
            extracted = True
        except Exception as e:
            logging.error(str(e))
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":str(e)})
            return 
        
        if not extracted:
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":"Something went wrong!"})
            return 
        
        verification_result = MODEL.compareEmbedding(list_of_features, features, sourcetype=sourcetype, tolerance = tolerance if tolerance != None else 0.4) 

        res.text = json.dumps(verification_result, default=str)


class VerifyFaceV2:
    def on_post(self, req, res):
        logging.info("Verify face V2 requested...")
        token = req.get_param("token")
        sha = req.get_param("sha")
        mode = req.get_param("mode")

        if(not DEBUG and (token == None or sha == None or sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest())):
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
            file_path = "{}/img/verify/{}-{}".format( os.getcwd() ,datetime.now().strftime("%Y%m%d-%H:%M:%S-%f"), incoming_file.filename)
            with open(file_path, "wb") as f:
                f.write(incoming_file.file.read())
            features = MODEL.extractFeatures(file_path, mode="native" if mode == None else mode)
            extracted = True
        except Exception as e:
            logging.error(str(e))
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":str(e)})
            return 
        
        if not extracted:
            res.status = falcon.HTTP_422
            res.text = json.dumps({"message":"Something went wrong!"})
            return 
        
        verification_result = MODEL.compareWithDistancesself(list_of_features, features, sourcetype=sourcetype, tolerance = tolerance if tolerance != None else 0.4) 

        res.text = json.dumps(verification_result, default=str)

class WebRegistration:
    def on_post(self, req, res):
        logging.info("Web registration requested...")
        token = req.get_param("token")
        sha = req.get_param("sha")
        mode = req.get_param("mode")

        if(not DEBUG and (token == None or sha == None or sha != hashlib.sha256((SECRET_KEY+token).encode()).hexdigest())):
            res.status = falcon.HTTP_401
            res.text = json.dumps({"message":"invalid access!"})
            return 

        incoming_files = req.get_param_as_list("faces")
        features = []
        for incoming_file in incoming_files:
            try:
                file_path = "{}/img/register/{}-{}".format( os.getcwd() ,datetime.now().strftime("%Y%m%d-%H:%M:%S-%f"), incoming_file.filename)
                with open(file_path, "wb") as f:
                    f.write(incoming_file.file.read())
                features.append(MODEL.extractFeatures(file_path,  output="list", mode="native" if mode == None else mode))
            except Exception as e:
                res.status = falcon.HTTP_422
                res.text = json.dumps({"message":str(e)})
                return 
        
        res.status = falcon.HTTP_200
        res.text = json.dumps(features)

class ServerStatus:
    def on_get(self, req, res):
        logging.info("Server status ok...")
        res.status = falcon.HTTP_200
        res.text = json.dumps({"message":"running normal"})


app = falcon.App(cors_enable = True,middleware=[MultipartMiddleware()])


def generic_error_handler(ex, req, resp, params):
    logging.error("An error occurred in request %s %s: %s", req.method, req.relative_uri, traceback.format_exc())
    raise falcon.HTTPInternalServerError(title="500 Internal Server Error", description=str(ex)) 

app.add_error_handler(Exception, generic_error_handler)

app.add_route("/register", RegisterFaces())
app.add_route("/web-register", WebRegistration())
app.add_route("/register-single", RegisterFace())
app.add_route("/verify", VerifyFace())
app.add_route("/v2/verify", VerifyFaceV2())
app.add_route("/status", ServerStatus())