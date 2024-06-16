import json
import os

import uvicorn
from PIL import Image

from fastapi import FastAPI, File
from fastapi.responses import RedirectResponse

from zipfile import ZipFile

from io import BytesIO

import os
from os import listdir
from os.path import isfile, join
import shutil


from ultralytics import YOLO

app = FastAPI()

model = YOLO("best.pt")

def model_predict(buf):
    return model.predict(buf)



def get_image_from_bytes(binary_image: bytes) -> Image:
    input_image = Image.open(BytesIO(binary_image)).convert("RGB")
    input_image = input_image.resize((640, 640))
    return input_image



def get_image_from_io(binary_image: BytesIO) -> Image:
    input_image = Image.open(binary_image).convert("RGB")
    input_image = input_image.resize((640, 640))
    return input_image




def zip_arh(arh):
    dir = "./ahr"
    if not os.path.isdir(dir):
        os.mkdir(dir)


    archive = 'file.zip'
    open(archive, "wb").write(arh)
    with ZipFile(archive, 'r') as zip_file:
        zip_file.extractall(dir)

    result = {
        "objects": []
    }

    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
    for k in onlyfiles:
        bfile = get_image_from_io(BytesIO(open(join(dir, k), 'rb').read()))

        predict = model_predict(bfile)
        if len(predict[0].boxes) > 0:
            for i in predict[0].boxes:
                xywhList = i.xywh.tolist()[0]
                result['objects'].append({
                    "class": predict[0].names[int(i.cls.tolist()[0])],
                    "x": round(xywhList[0], 1),
                    "y": round(xywhList[1], 1),
                    "width": round(xywhList[2], 1),
                    "height": round(xywhList[3], 1),
                    "confidence": i.conf.tolist()[0],
                    "filename": k
                })

    shutil.rmtree(dir)
    os.remove(archive)

    return result





def is_zip(file):
    try:
        zp = ZipFile(BytesIO(file))
        return True
    except Exception as _:
        return False






@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)





@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")



@app.post("/detect")
def img_object_detection_to_json(file: bytes = File()):
    if file == b'':
        return {}
    if is_zip(file):
        return zip_arh(file)
    else:
        input_image = get_image_from_bytes(file)

        result = {
            "objects": []
        }

        predict = model_predict(input_image)
        if len(predict[0].boxes) > 0:
            for i in predict[0].boxes:
                xywhList = i.xywh.tolist()[0]
                result['objects'].append({
                    "class": predict[0].names[int(i.cls.tolist()[0])],
                    "x": round(xywhList[0],1),
                    "y": round(xywhList[1],1),
                    "width": round(xywhList[2],1),
                    "height": round(xywhList[3],1),
                    "confidence": i.conf.tolist()[0],
                    "filename": ""
                })
        else:
            return {}

        return result




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)