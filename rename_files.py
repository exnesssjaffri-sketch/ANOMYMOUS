import os
import shutil

# Define the paths
source_path = "c:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\verification_new.py"
destination_path = "c:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\verification.py"

# Check if the source file exists
if not os.path.exists(source_path):
    print(f"Source file does not exist: {source_path}")
else:
    # Remove the destination file if it exists
    if os.path.exists(destination_path):
        os.remove(destination_path)
    
    # Rename the source file to the destination
    shutil.move(source_path, destination_path)
    print(f"File renamed from {source_path} to {destination_path}")