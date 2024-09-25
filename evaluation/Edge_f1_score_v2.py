from f1_score_funcs import *
import json
import glob

# Main function that finds similar edges between
# refernece graph and predicted graph.
def get_occurences(reference_json, prediction_json):
    occurences = {'true_positives':0, 'false_positives':0, 'false_negatives':0}
    
    #Access the node + edge fields for respective graphs
    reference_nodes = reference_json["nodes"]
    reference_edges = reference_json["edges"]
    prediction_nodes = prediction_json["nodes"]
    prediction_edges = prediction_json["edges"]
    
    for ref_edge in reference_edges:
        ref_source_id = ref_edge['source']
        ref_target_id = ref_edge['target']
        
        ref_label = ref_edge['label']
        ref_source_text = get_node_text_by_id(reference_nodes, ref_source_id)
        ref_target_text = get_node_text_by_id(reference_nodes, ref_target_id)

        for pred_edge in prediction_edges:
            pred_source_id = pred_edge['source']
            pred_target_id = pred_edge['target']

            pred_label = pred_edge['label']
            pred_source_text = get_node_text_by_id(prediction_nodes, pred_source_id)
            pred_target_text = get_node_text_by_id(prediction_nodes, pred_target_id)

            if match_function(pred_source_text, ref_source_text) and match_function(pred_target_text, ref_target_text) and pred_label.lower() == ref_label.lower():
                occurences['true_positives'] += 1
                break
    
    occurences['false_positives'] = len(prediction_edges) - occurences['true_positives']
    occurences['false_negatives'] = len(reference_edges) - occurences['true_positives']
    return occurences

def get_node_text_by_id(nodes, node_id):
    for node in nodes:
        if node['id'] == node_id:
            return node['text']

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

# print("Averaged Edge F1 score:\n" + str(get_avg_f1_score(calculate_metrics)))