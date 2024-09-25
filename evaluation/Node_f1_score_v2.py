from f1_score_funcs import *

def calculate_metrics(ref_graph, pred_graph):
    true_positives = 0
    for ref_node in ref_graph['nodes']:
        for pred_node in pred_graph['nodes']:
            if match_function(pred_node['text'], ref_node['text']):
                true_positives += 1
                break
    
    false_positives = len(pred_graph['nodes']) - true_positives
    false_negatives = len(ref_graph['nodes']) - true_positives

    precision = true_positives / (true_positives + false_positives) if pred_graph['nodes'] else 0
    recall = true_positives / (true_positives + false_negatives) if ref_graph['nodes'] else 0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

# print("Averaged Node F1 score:\n" + str(get_avg_f1_score(calculate_metrics)))