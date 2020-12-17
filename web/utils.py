"""
Utilities
"""
import os
import base64
import magic
import numpy as np
import cv2
from retinaface import RetinaFace
from descriptor import VectorExtractor
from sklearn.metrics.pairwise import cosine_similarity

os.environ["MXNET_CUDNN_AUTOTUNE_DEFAULT"]='0'
detector = RetinaFace(network='net3l')
models = [VectorExtractor(x) for x in [
    "vggf2_orig.onnx",             # 0.447739
    "balanced_pretrained.onnx",    # 0.453769
    "model_asian_2.onnx",    # 0.39045226 
    "model_indian_2.onnx",    # 0.4356783919
    "model_african_2.onnx"   # 0.396482

]]
tresholds = [0.447739, 0.453769, 0.390452, 0.65, 0.396482]

def get_alignment_rgb(img): # feed cv2 image
    im_scale = detector.get_scale(img)
    faces, landmarks = detector.detect(img,
                                scales=[im_scale],
                                do_flip=False)
    if faces.size > 0:
        face_id = np.argmax(faces[:, 4])
        face = faces[face_id]
        box = face[0:4].astype(np.int)

        dx = (box[2] - box[0])//5
        dy = (box[3] - box[1])//7
        x0 = max(0, box[0] - dx)
        y0 = max(0, box[1] - dy)
        y1 = min(img.shape[0], box[3] + dy)
        x1 = min(img.shape[1], box[2] + dx)

        img = img[y0:y1, x0:x1, ::-1]
    else:
        img = img[..., ::-1]
    return img # return rgb

def glue_and_prepare(img1, img2):
    img1 = cv2.resize(img1, (160, 160), interpolation=cv2.INTER_LINEAR)
    img2 = cv2.resize(img2, (160, 160), interpolation=cv2.INTER_LINEAR)
    img1 = np.expand_dims(np.transpose(img1, (2, 0, 1)), 0)
    img2 = np.expand_dims(np.transpose(img2, (2, 0, 1)), 0)
    img = (np.vstack((img1, img2)).astype(np.float32) - 127.5)/ 128.0
    return img

def compare(img, model_indices):
    result = []
    for i in model_indices:
        embeddings = models[int(i)].process(img.copy())[0]
        similarity = cosine_similarity(
            np.expand_dims(embeddings[0], 0),
            np.expand_dims(embeddings[1], 0))
        similarity = similarity - tresholds[int(i)]
        similarity = similarity**.5 if similarity >= 0 else - (-similarity)**.5
        result.append(similarity.item())

    return result        

def process_image(image):
    """
    Validate image and encode it to base64
    """

    valid_extensions = ["png", "jpg", "jpeg"]

    ext = magic.from_buffer(image).split(" ")[0].lower()

    if ext not in valid_extensions:
        return False

    # encoded = "" base64.b64encode(image)
    encoded = f"data:image/{ext};base64," + base64.b64encode(image).decode('ascii')

    return encoded

def decode_str_to_arr(image):
    """
    Decode bytes string to np array
    """

    decoded = cv2.imdecode(np.frombuffer(image, np.uint8), -1)

    return decoded

def process_form_data(form_data):
    """
    Call images validation
    """
    has_images = False
    if form_data.first_image and form_data.second_image:
        has_images = True
        form_data.first_image = process_image(form_data.first_image)
        form_data.second_image = process_image(form_data.second_image)

    if form_data.server_image_1 and form_data.server_image_2 and not has_images:
        form_data.first_image = process_server_file(form_data.server_image_1)
        form_data.second_image = process_server_file(form_data.server_image_2)

    if not form_data.first_image or not form_data.second_image:
        return False

    return form_data

def process_server_file(file_path):
    """
    Validate server images and encode it to base 64
    """

    valid_extensions = [".png", ".jpeg", ".jpg"]

    _, file_extension = os.path.splitext(file_path)
    if file_extension not in valid_extensions:
        return False

    with open(file_path, "rb") as fl:
        encoded = f"data:image/{file_extension};base64," + base64.b64encode(fl.read()).decode('ascii')

    return encoded