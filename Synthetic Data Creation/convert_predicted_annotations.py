import os
from text_to_json_and_back_scripts import *

# Directory containing the files
directory = 'predicted_annotations'

# List all files in the directory
files = os.listdir(directory)

# Iterate over each file
for file in files:
    # Check if the file is a text file
    if file.endswith('.txt'):
        # Read the contents of the file
        with open(os.path.join(directory, file), 'r') as f:
            essay = f.read()
        
        # Call the text_with_ids_to_json function
        result = text_with_ids_to_json(essay)
        
        # Write the result to a JSON file with the same name
        json_file = os.path.splitext(file)[0] + '.json'
        with open(os.path.join(directory, json_file), 'w') as f:
            json.dump(result, f, indent=2)