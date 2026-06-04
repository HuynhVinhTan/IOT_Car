import subprocess
import os

services_dir = r'd:\AA\IOT\project\smart_car\pc_app\backend\app\services'

mapping = {
    'car_control_service.py': 'robot',
    'robot_decision_service.py': 'robot',
    'joystick_service.py': 'robot',
    'remote_control_service.py': 'robot',
    'face_recognition_service.py': 'face',
    'cloudinary_media_service.py': 'media',
    'media_asset_service.py': 'media',
    'dataset_export_service.py': 'ai',
    'training_sample_service.py': 'ai',
    'training_session_service.py': 'ai'
}

for filename, subfolder in mapping.items():
    print(f'Recovering {filename} to {subfolder}...')
    try:
        content = subprocess.check_output(
            ['git', '--no-pager', 'show', f'HEAD:pc_app/backend/app/services/{filename}'],
            cwd=r'd:\AA\IOT\project\smart_car',
            text=True,
            encoding='utf-8'
        )
        
        target_dir = os.path.join(services_dir, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, filename)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f'  -> Wrote {len(content)} bytes to {target_path}')
        
        shim_path = os.path.join(services_dir, filename)
        if not os.path.exists(shim_path):
            class_name = ''.join(word.capitalize() for word in filename[:-3].split('_'))
            # Special case for CloudinaryMediaService
            if class_name == 'CloudinaryMediaService':
                with open(shim_path, 'w', encoding='utf-8') as f:
                    f.write(f'from app.services.media.cloudinary_media_service import CloudinaryMediaService, MediaUploadResult\n\n__all__ = ["CloudinaryMediaService", "MediaUploadResult"]\n')
            else:
                with open(shim_path, 'w', encoding='utf-8') as f:
                    f.write(f'from app.services.{subfolder}.{filename[:-3]} import {class_name}\n\n__all__ = ["{class_name}"]\n')
            print(f'  -> Created shim at {shim_path}')
            
    except subprocess.CalledProcessError as e:
        print(f'  -> ERROR getting file from git: {e}')