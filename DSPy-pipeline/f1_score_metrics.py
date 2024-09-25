import os
import sys
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'datasets', 'utility_scripts')))
from text_to_json_and_back_scripts import * # type: ignore

def dspy_metric(example, pred, trace=None):
    try:
        node_f1_score = calculate_node_metrics(example, pred)['f1_score']
        edge_f1_score = calculate_edge_metrics(example, pred)['f1_score']

        if not isinstance(node_f1_score, float):
            node_f1_score = 0
        if not isinstance(edge_f1_score, float):
            edge_f1_score = 0

        print("Node F1 Score: ", node_f1_score)
        print("Edge F1 Score: ", edge_f1_score)
        print("Output Metric: ", 0.15 * node_f1_score + 0.85 * edge_f1_score)
        return 0.15 * node_f1_score + 0.85 * edge_f1_score
    except Exception as e:
        print("Error in output metric: ", e)
        return 0

def graph_output_metric(example, pred, trace=None):
    dspy_metric(example.graph, pred.graph)
    
def annotations_output_metric(example, pred, trace=None):
    try:
        example_graph = text_with_ids_to_json(example.annotated_essay) # type: ignore
        pred_graph = text_with_ids_to_json(pred.annotated_essay) # type: ignore
    except Exception as e:
        print("Error converting output to graph: ", e)
        return 0
    dspy_metric(example_graph, pred_graph)

def calculate_node_metrics(ref_graph, pred_graph):
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


def calculate_edge_metrics(json_ref, json_pred):
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

def match_function(pred, ref):
    THRESHOLD = 0.75
    
    # tokenization
    pred_list = word_tokenize(pred)  
    ref_list = word_tokenize(ref) 
    
    # sw contains the list of stopwords 
    sw = stopwords.words('english')  
    l1 =[];l2 =[] 
    
    # remove stop words from the string 
    pred_set = {w for w in pred_list if not w in sw}  
    ref_set = {w for w in ref_list if not w in sw} 
    
    # form a set containing keywords of both strings  
    rvector = pred_set.union(ref_set)  
    for w in rvector: 
        if w in pred_set: l1.append(1) # create a vector 
        else: l1.append(0) 
        if w in ref_set: l2.append(1) 
        else: l2.append(0) 
    c = 0
    
    # cosine formula  
    for i in range(len(rvector)): 
            c+= l1[i]*l2[i] 
    cosine = c / float((sum(l1)*sum(l2))**0.5) 
    # if (cosine < THRESHOLD):
    #     print(pred)
    #     print(ref)
    return cosine >= THRESHOLD