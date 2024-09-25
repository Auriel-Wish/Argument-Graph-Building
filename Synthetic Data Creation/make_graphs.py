import json
import os

input_file = 'all_annotations.json'

def make_new_edge(relation, from_id, to_id):
    return {
        "label": relation,
        "source": from_id,
        "target": to_id
    }

with open(input_file, 'r') as f:
    total_json = json.loads(f.read())
    for essay in total_json:
        file_string = essay["file_upload"]
        out_file_name = file_string.split('-')[1].split('.')[0]
        graph = {"nodes":[], "edges":[]}
        id_correlation = {}
        i = 0
        for result in essay["annotations"][0]["result"]:
            if "value" in result:
                text = result["value"]["text"]
                adu_type = result["value"]["labels"][0]
                node = {'text':text, 'id':result["id"], 'type':adu_type}
                i += 1
                graph["nodes"].append(node)
            else:
                if "labels" in result:
                    if len(result["labels"]) > 0:
                        if "support" in result["labels"][0].lower():
                            graph["edges"].append(make_new_edge("support", result["from_id"], result["to_id"]))
                        elif "attack" in result["labels"][0].lower():
                            graph["edges"].append(make_new_edge("attack", result["from_id"], result["to_id"]))
        for i, node in enumerate(graph["nodes"]):
            curr_id = node["id"]
            changed_id = "N" + str(i + 1)
            for edge in graph["edges"]:
                if edge["source"] == curr_id:
                    edge["source"] = changed_id
                if edge["target"] == curr_id:
                    edge["target"] = changed_id
            node["id"] = changed_id
        with open(os.path.join("Annotated_Data", "JSON", (out_file_name + '.json')), 'w') as out_file:
            out_file.write(json.dumps(graph, indent=2))
        with open(os.path.join("Annotated_Data", "Raw-Text", (out_file_name + '.txt')), 'w') as out_file:
            out_file.write(essay["data"]["text"])