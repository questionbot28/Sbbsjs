
import os
import zipfile
from datetime import datetime

def create_bot_zip():
    # Get current timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"discord_bot_{timestamp}.zip"
    
    # Define files/folders to exclude
    exclude = {'.git', '__pycache__', '.env', '.upm', '.config', '.cache', '.replit', 'replit.nix', '.pytest_cache'}
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all directories
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                # Skip excluded files and zip files
                if file.startswith('.') or file.endswith('.zip'):
                    continue
                    
                file_path = os.path.join(root, file)
                # Add file to zip with relative path
                arc_name = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_name)
    
    print(f"Bot files have been zipped to: {zip_filename}")
    return zip_filename

if __name__ == "__main__":
    create_bot_zip()
