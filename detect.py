import cv2
import numpy as np

def crop_mrz_region(path):
    img = cv2.imread(path)
    mrz_region = get_mrz_region(img)
    x,y,w,h = mrz_region
    crop_img = img[y:y+h, x:x+w]
    cv2.imshow("cropped", crop_img)
    cv2.imwrite("cropped.jpg",crop_img)
    cv2.waitKey(0)
    

def get_mrz_region(img):
    cv2.namedWindow("output", cv2.WINDOW_NORMAL)
    mser = cv2.MSER_create()
    vis = img.copy()
    
    vis = cv2.resize(vis, (720, 720), interpolation = cv2.INTER_AREA)
    
    scale_x = img.shape[1]/720
    scale_y = img.shape[0]/720
    
    gray = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)

    img_width = vis.shape[1]
    img_height = vis.shape[0]

    
    regions, boundingBoxes  = mser.detectRegions(gray)
    boxes = filtered_boxes_by_size(boundingBoxes, img_width, img_height)
    remove_outer_boxes(boxes)
    boxes = merge_boxes_to_lines(boxes)
    mrz_region = last_two_lines_merged(boxes)
    expand(15, mrz_region,img_width,img_height)
    x,y,w,h = mrz_region
    cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 1)

    cv2.imshow('output', vis)
    cv2.waitKey(0)
    revert_region(scale_x, scale_y, mrz_region)
    return mrz_region
    
def revert_region(scale_x,scale_y,box):
    box[0] = int(box[0] * scale_x)
    box[1] = int(box[1] * scale_y)
    box[2] = int(box[2] * scale_x)
    box[3] = int(box[3] * scale_y)

def last_two_lines_merged(boxes):
    boxes = sorted(boxes, key=lambda x:x[1])
    if len(boxes)>=2:
        return merged_box(boxes[-2],boxes[-1])
    else:
        return boxes[0]
        
def expand(pixel, box, img_width, img_height):
    x,y,w,h = box
    maxX = x + w
    maxY = y + h
    new_x = max(0, x-pixel)
    new_y = max(0, y-pixel)
    new_maxX = min(img_width, maxX+pixel)
    new_maxY = min(img_height, maxY+pixel)
    box[0] = new_x
    box[1] = new_y
    box[2] = new_maxX - new_x
    box[3] = new_maxY - new_y
    


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
        for j in range(len(boxes)):  
            box1 = boxes[i]
            box2 = boxes[j]
            if area_of_box(box1)<area_of_box(box2):
                index = j
                
            if intersection_area(box1,box2)>0:
                boxes_index_to_remove.add(index) # remove larger boxes
    list1 = list(boxes_index_to_remove)
    list1.sort(reverse=True) # remove from the end 
    for index in list1:
        boxes.pop(index)
            
       
def merge_boxes_to_lines(boxes):
    boxes = sorted(boxes, key=lambda x:x[1])
    boxes = sorted(boxes, key=lambda x:x[0])
    new_boxes = []
    while len(boxes)>0:
        box = boxes[0]    
        merged = merge_boxes_belong_to_one_line(box, boxes)
        if merged == None:
            boxes.remove(box)
        else:
            new_boxes.append(merged)
    return new_boxes


def merge_boxes_belong_to_one_line(box, boxes):
    boxes_index_can_be_merged = set()
    for i in range(len(boxes)): 
        target_box = boxes[i]
        if i == 0: #the box itself
            continue
        if boxes_in_one_line(box, target_box):
            boxes_index_can_be_merged.add(i)
    
    if len(boxes_index_can_be_merged) == 0:
        return None
        
    filtered_boxes = []
    filtered_boxes.append(box)
    for i in boxes_index_can_be_merged:
        filtered_boxes.append(boxes[i])
    
    right_index = get_right_most_index(filtered_boxes)
    right_most_box = filtered_boxes[right_index]
    
    left_index = get_left_most_index(filtered_boxes)
    left_most_box = filtered_boxes[left_index]
    
    merged = merged_box(left_most_box, right_most_box)
    
    list1 = list(boxes_index_can_be_merged)
    list1.sort(reverse=True) # remove from the end 
    for i in list1:
        boxes.pop(i)
    
    return merged
    
def get_left_most_index(boxes):
    minX = boxes[0][0]
    left_most_index = 0
    for i in range(len(boxes)):
        box = boxes[i]
        box_left = box[0]
        if box_left<minX:
            minX = box_left
            left_most_index = i
    return left_most_index
    
def get_right_most_index(boxes):
    maxX = 0
    right_most_index = 0
    for i in range(len(boxes)):
        box = boxes[i]
        box_right = box[0] + box[2]
        if box_right>maxX:
            maxX = box_right
            right_most_index = i
    return right_most_index

def boxes_in_one_line(a, b):
    y = max(a[1], b[1])
    max_y1 = a[1]+a[3]
    max_y2 = b[1]+b[3] 
    intersect_h = min(max_y1, max_y2) - y
    if intersect_h>-10:
        return True
    else:
        return False
    
    
def merged_box(box1, box2):
    minX = min(box1[0], box2[0])
    maxX = max(box1[0]+box1[2], box2[0]+box2[2])
    minY = min(box1[1], box2[1])
    maxY = max(box1[1]+box1[3], box2[1]+box2[3])
    new_box = [minX, minY, maxX-minX, maxY-minY]
    return new_box
    
    
crop_mrz_region("9e4e9ab49713b37ad055e460bfc1f434.jpg")