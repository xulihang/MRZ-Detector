import cv2
import numpy as np

def get_boxes(path):
    cv2.namedWindow("output", cv2.WINDOW_NORMAL)
    mser = cv2.MSER_create()
    img = cv2.imread(path)
    img = cv2.resize(img, (720, 720), interpolation = cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img_width = img.shape[0]
    img_height = img.shape[1]

    vis = img.copy()
    regions, boundingBoxes  = mser.detectRegions(gray)
    boxes = filtered_boxes_by_size(boundingBoxes, img_width, img_height)
    remove_outer_boxes(boxes)

    for box in boxes:
        x, y, w, h = box
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 1)

    cv2.imshow('output', vis)
    cv2.waitKey(0)
    return boxes

def filtered_boxes_by_size(boundingBoxes, img_width, img_height):
    filtered_boxes = []
    for box in boundingBoxes:
        x, y, w, h = box
        if w>img_width/4:
            continue
        if h>img_height/4:
            continue
        filtered_boxes.append(box)
    return filtered_boxes

def larger_and_smaller_box(box1,box2):
    if area_of_box(box1)>area_of_box(box2):
        return box1, box2
    else:
        return box2, box1

def area_of_box(box):
    return box[2]*box[3]

def intersection_area(a,b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0]+a[2], b[0]+b[2]) - x
    h = min(a[1]+a[3], b[1]+b[3]) - y
    if w<0 or h<0: return 0
    return w*h
    
def remove_outer_boxes(boxes):
    boxes_index_to_remove=set()
    for i in range(len(boxes)):
        index = i
        if i in boxes_index_to_remove:
            continue
        for j in range(len(boxes)):
            if j in boxes_index_to_remove:
                continue    
            box1 = boxes[i]
            box2 = boxes[j]
            if area_of_box(box1)<area_of_box(box2):
                index = j
                
            if intersection_area(box1,box2)>0:
                boxes_index_to_remove.add(index) # remove larger boxes
    list1 = list(set(boxes_index_to_remove))
    list1.sort(reverse=True) # remove from the end 
    for index in list1:
        boxes.pop(index)
            
            

def merge_boxes_to_lines(boxes):
    for box in boxes:
        print(box)
    
    
def merged_box(box1, box2):
    print("")
    
    
get_boxes("1175418_231184000363788_534965287_n.png")