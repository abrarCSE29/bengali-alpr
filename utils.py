import cv2
import os
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DETECTION_FOLDER = 'detection'
os.makedirs(DETECTION_FOLDER, exist_ok=True)

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        print(f"load_image(): {path} not found")
    return img


import imutils
def resize_image(img, max_width = 500):
    if img is None:
        print(f'resize_image(): img is null')
        return
    if img.shape[0] > maxwidth:
        img = imutils.resize(img, maxwidth)
    return img


from matplotlib import pyplot as plt
def show_image(img):
    plt.axis("off")
    if isinstance(img, str):
        img = cv2.imread(img)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))



from ultralytics.models import YOLO
model = YOLO('models/yolo.pt')
def detect_license_plate(img):
    detection = model.predict(img, conf=0.5, verbose=False)
    if detection is None:
        print(f"detect_license_plate(): img is null")
        return
    return detection[0]


# Function to put Bengali text on image using PIL
def put_bengali_text(img, text, position, font_size=64, text_color=(255,0, 0)):
    # Convert OpenCV image (BGR) to PIL image (RGB)
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Try to load NirmalaUI font which has good Bengali support on Windows
    try:
        # Try NirmalaUI font which is available on Windows 10/11
        font = ImageFont.truetype("fonts\\kalpurush.ttf", font_size)
        print(font)
    except:
        try:
            # Try regular Nirmala font if Bold is not available
            font = ImageFont.truetype("Nirmala UI.ttf", font_size, encoding="unic")
        except:
            try:
                # Try without UI suffix
                font = ImageFont.truetype("Nirmala.ttf", font_size)
            except:
                # Fallback to default
                font = ImageFont.load_default()
                print("Warning: Could not load NirmalaUI font. Text may not display correctly.")
    
    # Draw text on image
    draw.text(position, text, font=font, fill=text_color)
    
    # Convert back to OpenCV format (BGR)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


from extract_license_text import extract_license_text
def detect_and_extract_lp_text(path, show_cropped_image = True, draw_bbox = True):
    img = load_image(path)
    detection_result = detect_license_plate(img)
    bbox = detection_result.boxes.data.numpy()
    xmin, ymin = bbox[0][:2].astype(int)
    xmax, ymax = bbox[0][2:4].astype(int)
    cropped_img = img[ymin:ymax, xmin:xmax]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    cropped_filename = os.path.join(DETECTION_FOLDER, f"cropped_{timestamp}.jpg")
    cv2.imwrite(cropped_filename, cropped_img)        
    lp_text = extract_license_text(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)).decode('utf-8')
    
    # Draw bounding box and text on the original image if requested
    if draw_bbox:
        img_with_bbox = img.copy()
        # Draw rectangle
        cv2.rectangle(img_with_bbox, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        
        # Use the Bengali text function instead of cv2.putText
        text_x = xmin
        text_y = ymin - 40 if ymin > 40 else ymin + 40  # Place text above or below depending on position
        
        # Add Bengali text to the image
        img_with_bbox = put_bengali_text(
            img_with_bbox, 
            lp_text, 
            (text_x, text_y - 30),  # Adjust position for PIL
            font_size=32, 
            text_color=(255,0, 0)
        )
        
        # Save the image with bounding box
        bbox_filename = os.path.join(DETECTION_FOLDER, f"bbox_{timestamp}.jpg")
        cv2.imwrite(bbox_filename, img_with_bbox)
        
        # Show the image with bounding box if requested
        if show_cropped_image:
            plt.figure(figsize=(10, 8))
            plt.imshow(cv2.cvtColor(img_with_bbox, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        
        return lp_text, img_with_bbox
    
    return lp_text