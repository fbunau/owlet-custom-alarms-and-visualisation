import easyocr
import numpy as np
import pyscreenshot as ImageGrab
import cv2

from datetime import datetime
import functools

from util import map_vals

def get_ocr_model():
  return easyocr.Reader(['ch_sim','en'], gpu = True)

def preproc_image(im):
  im_np = np.array(im)
  scale_percent = 50
  width = int(im_np.shape[1] * scale_percent / 100)
  height = int(im_np.shape[0] * scale_percent / 100)
  dim = (width, height)
  return cv2.resize(im_np, dim, interpolation = cv2.INTER_AREA)

def pipeline(reader, x):
  try:
    return reader.readtext(np.array(preproc_image(ImageGrab.grab(bbox=x.to_tuple()))))[0][1]
  except:
    return None
  
def read_data(config, reader):
  return {
    **{ "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S") },
    **dict(map_vals(config.label_locations.items(), functools.partial(pipeline, reader)))
  }