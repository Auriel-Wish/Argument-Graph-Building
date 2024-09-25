import os
import json

def convert_text_files_to_json(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
                with open(filename.split('.')[0] + '.json', 'w', encoding='utf-8') as json_file:
                    json_file.write(json.dumps({"data": {"text": text_content}}, indent=4))

if __name__ == "__main__":
    convert_text_files_to_json("Generated_Data/Raw-Text")
    print("All text files have been converted to data.json")
