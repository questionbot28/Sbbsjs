import os
import zipfile
from datetime import datetime

def create_export_zip():
    # Essential files and directories to include
    essential_files = [
        'main.py',
        'keep_alive.py',
        'cogs',
        'utils',
        'requirements.txt',
        '.env.example'
    ]
    
    # Create zip filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'discord_bot_glitch_{timestamp}.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add essential files
        for file_or_dir in essential_files:
            if os.path.isfile(file_or_dir):
                zipf.write(file_or_dir)
            elif os.path.isdir(file_or_dir):
                for root, dirs, files in os.walk(file_or_dir):
                    # Skip __pycache__ directories
                    if '__pycache__' in dirs:
                        dirs.remove('__pycache__')
                    for file in files:
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path)
    
    return zip_filename

if __name__ == "__main__":
    zip_file = create_export_zip()
    print(f"Project exported to: {zip_file}")
