import json
import re
import glob

THRESHOLD = 0.5

# Checks if two given sentences are patially matching or not
def partial_match(sentence1, sentence2):
    if sentence1 is None or sentence2 is None:
        return False
    
    pattern = re.compile(r'\b\w+\b')
    span1 = pattern.findall(sentence1)
    span2 = pattern.findall(sentence2)
    
    #If more than half of the the sentence is a match, we return True
    count = len(set(span1) & set(span2))
    return count > THRESHOLD * len(span1)


#Iterates thru the the respective nodes field and finds
#the index of the corresponding text in that node field
def find_node_index_by_text(nodes, text):
    for i, node in enumerate(nodes):
        if partial_match(node.get('text'), text):
            return i
    return -1


# Main function that finds similar edges between
# refernece graph and predicted graph.
def get_occurences(reference_json, prediction_json):
    occurences = {'true_positives':0, 'false_positivs':0, 'false_negatives':0}
    
    #Access the node + edge fields for respective graphs
    reference_nodes = reference_json["nodes"]
    reference_edges = reference_json["edges"]
    prediction_nodes = prediction_json["nodes"]
    prediction_edges = prediction_json["edges"]
    
    
    for ref_edge in reference_edges:
        
        #Get curr reference edge's source & target idx and the label (support/attack)
        ref_source_index = ref_edge['source']
        ref_target_index = ref_edge['target']
        ref_label = ref_edge['label']
        
        #Get the text corresponding to the source & target idx in the reference nodes field
        ref_source_text = reference_nodes[ref_source_index].get('text')
        ref_target_text = reference_nodes[ref_target_index].get('text')
        
        
        #If we find a similar src reference in the predicted nodes field
        #then, find the index of that text in the predicted nodes field
        pred_source_index = find_node_index_by_text(prediction_nodes, ref_source_text)
        if pred_source_index == -1:
            continue
        
        #If we find a similar target reference in the predicted nodes field
        #then, find the index of that text in the predicted nodes field
        pred_target_index = find_node_index_by_text(prediction_nodes, ref_target_text)
        if pred_target_index == -1:
            continue
        
        #Create a tuple of the possible source -> target indices
        pair = (pred_source_index, pred_target_index)
        #check all the edges in the predicted edges field and see if any such pair exists
        #in any of the edges source and target
        exists = any(
            (edge['source'] == pair[0] and edge['target'] == pair[1] and edge['label'] == ref_label)
            for edge in prediction_edges
        )
        
        if exists:
            occurences['true_positives'] += 1
    
    occurences['false_positives'] = len(prediction_edges) - occurences['true_positives']
    occurences['false_negatives'] = len(reference_edges) - occurences['true_positives']
    return occurences

def calculate_metrics(json_ref, json_pred):
    occurences = get_occurences(json_ref, json_pred)
    true_positives = occurences['true_positives']
    false_positives = occurences['false_positives']
    false_negatives = occurences['false_negatives']

    precision = float('%.3f'%(true_positives / (true_positives + false_positives) if true_positives + false_positives > 0 else 0))
    recall = float('%.3f'%(true_positives / (true_positives + false_negatives) if true_positives + false_negatives > 0 else 0))
    f1_score = float('%.3f'%(2 * precision * recall / (precision + recall) if precision + recall > 0 else 0))

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

def get_scores():
    all_scores = []

    # Change this depending on which model's predictions you want to check
    pred_dir_name = "Datasets/Zero-Shot-Predicted-JSON"
    ref_dir_name = "Datasets/Synthetic/Reference-JSON"
    
    prediction_dir = glob.glob(pred_dir_name + "/*")
    reference_dir = glob.glob(ref_dir_name + "/*")

    for dir in prediction_dir:
        for dir2 in reference_dir:
            if (dir.split("/")[-1] == dir2.split("/")[-1]):
                pred_dataset_dir = glob.glob(dir + "/*")
                for path in pred_dataset_dir:
                    curr_ref_path = ref_dir_name + "/" + path.split("/")[-2] + "/" + path.split("/")[-1]
                    with open(path, 'r') as pred_f:
                        with open(curr_ref_path, 'r') as ref_f:
                            pred_json = json.loads(pred_f.read())
                            ref_json = json.loads(ref_f.read())
                            curr_score = calculate_metrics(ref_json, pred_json)
                            print(curr_score)
                            all_scores.append(curr_score)
            # break # REMOVE LATER
    return all_scores

def average(all_scores):
    total_precision = 0
    total_recall = 0
    total_f1 = 0
    length = len(all_scores)
    for score in all_scores:
        total_precision += score['precision']
        total_recall += score['recall']
        total_f1 += score['f1_score']
    
    return {
        'precision': float('%.3f'%(total_precision / length)),
        'recall': float('%.3f'%(total_recall / length)),
        'f1_score': float('%.3f'%(total_f1 / length))
    }

score = average(get_scores())
print(score)