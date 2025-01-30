import os
import json
from scipy.interpolate import interp1d
import numpy as np
from PIL import Image
import argparse
# Your camera data

#scene_list = ['bicycle','bonsai','drjohnson','flowers','kitchen','playroom','room','stump','train','treehill','truck']
scene_list = ['garden']


def generate_camera_trace(scene_name, input_camera_path, output_dir, mode='limit'):
    """
    Generate smooth camera trace for scene interpolation

    Args:
        scene_name (str): Name of the scene
        input_camera_path (str): Path to input camera json file
        output_base_path (str): Base path for output folder
        mode (str): 'full' for first 40 cameras, 'limit' for first 2 cameras
    """
    scene_info = {
        'bicycle': {'downscale': 4, 'width': 1237, 'height': 822},
        'flowers': {'downscale': 4, 'width': 1256, 'height': 828},
        'stump': {'downscale': 4, 'width': 1245, 'height': 825},
        'treehill': {'downscale': 4, 'width': 1267, 'height': 832},
        'garden': {'downscale': 4, 'width': 1297, 'height': 840},
        'bonsai': {'downscale': 2, 'width': 1559, 'height': 1039},
        'kitchen': {'downscale': 2, 'width': 1558, 'height': 1039},
        'room': {'downscale': 2, 'width': 1557, 'height': 1038},
        'train': {'downscale': 2, 'width': 980, 'height': 545},
        'truck': {'downscale': 2, 'width': 979, 'height': 546},
        'drjohnson': {'downscale': 1, 'width': 1332, 'height': 876},
        'playroom': {'downscale': 1, 'width': 1264, 'height': 832}
    }

    scene_params = scene_info.get(scene_name, {'downscale': 1, 'width': 1920, 'height': 1080})
    downscale = scene_params['downscale']

    # Load cameras
    with open(input_camera_path, 'r') as fcam:
        cams = json.load(fcam)
    sorted_cameras = sorted(cams, key=lambda x: x['img_name'][-4:])

    if mode == 'full':
        cameras = sorted_cameras[:40]
        frames_per_segment = 120
        save_mode = 'smooth'
    else:
        cameras = sorted_cameras[:2]
        frames_per_segment = 1200
        save_mode = 'limit'

    total_cameras = len(cameras)
    interpolated_cameras = []
    for i in range(total_cameras - 1):
        start_cam, end_cam = cameras[i], cameras[i + 1]
        segment_time_scale = np.linspace(0, 1, frames_per_segment)

        position_interp = interp1d([0, 1], np.array([start_cam['position'], end_cam['position']]), axis=0)
        rotation_interp = interp1d([0, 1], np.array([start_cam['rotation'], end_cam['rotation']]), axis=0)

        for t in segment_time_scale[:]:
            if t == 0:
                camera = {
                    "id": start_cam["id"],
                    'img_name': cameras[i]['img_name'],
                    "width": scene_params['width'],
                    "height": scene_params['height'],
                    "position": cameras[i]['position'],
                    "rotation": cameras[i]['rotation'],
                    "fy": start_cam["fy"] / downscale,
                    "fx": start_cam["fx"] / downscale,
                    "is_key_frame": True
                }
            else:
                camera = {
                    "id": start_cam["id"],
                    'img_name': start_cam['img_name'],
                    "width": scene_params['width'],
                    "height": scene_params['height'],
                    "position": position_interp(t).tolist(),
                    "rotation": rotation_interp(t).tolist(),
                    "fy": start_cam["fy"] / downscale,
                    "fx": start_cam["fx"] / downscale,
                    "is_key_frame": False
                }
            interpolated_cameras.append(camera)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save to JSON file with mode-specific filename
    output_filename = f"{save_mode}_camera_trace.json"
    output_file = os.path.join(output_dir, output_filename)
    with open(output_file, 'w') as f:
        json.dump(interpolated_cameras, f, indent=4)

    print(f"Generated {len(interpolated_cameras)} camera positions")
    print(f"Smooth camera trace saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate smooth camera trace for scene interpolation')
    parser.add_argument('--scene_name', type=str, required=True, help='Name of the scene')
    parser.add_argument('--input_camera_path', type=str, required=True, help='Path to input camera json file')
    parser.add_argument('--output_folder', type=str, required=True, help='Base path for output folder')
    parser.add_argument('--mode', type=str, choices=['full', 'limit'], default='limit',
                        help='Mode of operation: "full" for 40 cameras, "limit" for 2 cameras')

    args = parser.parse_args()

    generate_camera_trace(
        scene_name=args.scene_name,
        input_camera_path=args.input_camera_path,
        output_dir=args.output_folder,
        mode=args.mode
    )

if __name__ == "__main__":
    main()
