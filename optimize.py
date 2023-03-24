from PIL import Image
import fitz
import numpy as np
import argparse
import random
import string
import shutil
import cv2
import sys
import os
      

def pdf_to_img(pdf_path, tmpfolder="."):
  # To get better resolution
  zoom_x = 2.0  # horizontal zoom
  zoom_y = 2.0  # vertical zoom
  mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

  pdf_name = os.path.basename(pdf_path)
  
  # for filename in all_files:
  names = []
  doc = fitz.open(pdf_path)  # open document
  for page in doc:  # iterate through the pages
    name = os.path.join(tmpfolder, f"{pdf_name}-{page.number}.png")
    names.append(name)
    pix = page.get_pixmap(matrix=mat)  # render page to an image
    pix.save(name)  # store image as a PNG

  return names

def img_to_pdf(imgnames, pdf_path="new.pdf"):
  pdf_img_list = []
  for name in imgnames:
    img = Image.open(name)
    pdf_img_list.append(img.convert('RGB'))

  pdf_img_list[0].save(pdf_path, save_all=True, append_images=pdf_img_list[1:])
  
##------------------------------------------------------------
def remove_shadow(img_path):
  # img_name = os.path.basename(img_path)

  img = cv2.imread(img_path, -1)
  rgb_planes = cv2.split(img)

  result_norm_planes = []
  for plane in rgb_planes:
    dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
    bg_img = cv2.medianBlur(dilated_img, 21)
    diff_img = 255 - cv2.absdiff(plane, bg_img)
    norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    result_norm_planes.append(norm_img)
      
  result_norm = cv2.merge(result_norm_planes)
  cv2.imwrite(img_path, result_norm)
  
  return img_path


"""
rotate function rotate the scaned image according to the text orientation
https://pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
"""
def rotate(img_path, horizontal=True, threshold=10):

  image = cv2.imread(img_path)
  # convert the image to grayscale and flip the foreground
  # and background to ensure foreground is now "white" and
  # the background is "black"
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  gray = cv2.bitwise_not(gray)
  # threshold the image, setting all foreground pixels to
  # 255 and all background pixels to 0
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
  
  # grab the (x, y) coordinates of all pixel values that
  # are greater than zero, then use these coordinates to
  # compute a rotated bounding box that contains all
  # coordinates
  coords = np.column_stack(np.where(thresh > 0))
  angle = cv2.minAreaRect(coords)[-1]
  # the `cv2.minAreaRect` function returns values in the
  # range [-90, 0); as the rectangle rotates clockwise the
  # returned angle trends to 0 -- in this special case we
  # need to add 90 degrees to the angle
  if angle < -45:
    angle = -(90 + angle)
  else:
    angle = -angle

  # rotate the image according to text writting direction
  if not horizontal:
    if angle < 0:
      pass
    else:
      angle += 90
  
  if abs(angle) > threshold:
    print(f"detected {angle} rotation required {img_path}. treat as error.")

  else:
    # rotate the image to deskew it
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


    # draw the correction angle on the image so we can validate it
    # cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # show the output image
    print("rotated {} {:.3f}".format(img_path, angle))
    # cv2.imshow("Input", image)
    # cv2.imshow("Rotated", rotated)
    # cv2.waitKey(0)
  
    cv2.imwrite(img_path, rotated)
  
          
  return img_path


def optimize(pdf_path, horizontal=True, rotate_threshold=10):
  tmpfolder = '__' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
  os.mkdir(tmpfolder)
  print(f"created tmp folder: {tmpfolder}")
        
  # convert the pdf into png first
  img_list = pdf_to_img(pdf_path, tmpfolder)

  #
  for img_name in img_list:
    remove_shadow(img_name)
    rotate(img_name, horizontal, rotate_threshold)

  # convert iamge back to pdf
  output_pdf_dir = os.path.dirname(pdf_path)
  pdf_name = os.path.basename(pdf_path)
  
  img_to_pdf(img_list, os.path.join(output_pdf_dir, f"new-{pdf_name}"))

  print("deleting temp folder...")
  shutil.rmtree(tmpfolder)
  print(" done")

if __name__ == "__main__":
  
  optimize(sys.argv[1], False, 2.5)

