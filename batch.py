import os
import detector
import cv2

def is_image(filename):
    name, ext = os.path.splitext(filename)
    if ext.lower() in ('.png','.jpg','.jpeg','.bmp'):
        return True
    else:
        return False

def convert_folder(path, saved_folder):
    if os.path.exists(saved_folder) == False:
        os.mkdir(saved_folder)
    for filename in os.listdir(path):
        if is_image(filename):
            cropped = detector.crop_mrz_region(os.path.join(path, filename))
            cv2.imwrite(os.path.join(saved_folder,filename),cropped)
            
            
if __name__ == "__main__":
    convert_folder("dataset","dataset-cropped")