import shutil

# Define the paths
source_path = "c:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\verification_fixed.py"
destination_path = "c:\\Users\\ALI HAIDER\\OneDrive\\Desktop\\ANOMYMOUS\\verification.py"

# Copy the file
shutil.copy2(source_path, destination_path)

print(f"File copied from {source_path} to {destination_path}")