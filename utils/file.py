import os
import shutil
import json

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def copy_image_and_json_to_sfm(image_path, json_data, sfm_img_dir, sfm_meta_dir):
    ensure_dir(sfm_img_dir)
    ensure_dir(sfm_meta_dir)

    filename = os.path.basename(image_path)
    name, _ = os.path.splitext(filename)

    shutil.copy(image_path, os.path.join(sfm_img_dir, filename))

    with open(os.path.join(sfm_meta_dir, f"{name}.json"), "w") as f:
        json.dump(json_data, f, indent=2)
