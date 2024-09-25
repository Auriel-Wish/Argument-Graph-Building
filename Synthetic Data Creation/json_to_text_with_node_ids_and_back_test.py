import os
import glob
import json

from text_to_json_and_back_scripts import *
from graph_equivalency import check_isomorphism

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_essay(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def process_json_files(directory):
    error_files = []
    success_files = []
    failure_files = []

    json_files = glob.glob(os.path.join(directory, "*.json"))
    for json_file in json_files:
        fname = os.path.basename(json_file).split(".")[0]
        try:
            essay = get_essay(f"Original_Data/Raw-Text/{fname}.txt")

            json_data = load_json(json_file)
            # Convert JSON to text with node IDs
            text_with_ids = json_to_text_with_node_ids(json_data, essay)

            # Convert text back to JSON
            converted_json_data = text_with_ids_to_json(text_with_ids)
            isomorphic = check_isomorphism(json_data, converted_json_data)
            if not isomorphic:
                print(f"Graphs are NOT equivalent for {json_file}")
                failure_files.append(fname)
            else:
                with open('with_node_ids/' + fname + '_with_node_ids.txt', 'w') as file:
                    file.write(text_with_ids)
                print(f"Graphs are equivalent for {json_file}")
                success_files.append(fname)
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            error_files.append(fname)
        
    print(f"Success: {len(success_files)}")
    print(f"Failure: {len(failure_files)}")
    print(f"Error: {len(error_files)}")

if __name__ == "__main__":
    directory = "Original_Data/Reference-JSON"
    process_json_files(directory)