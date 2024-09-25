import json
import os
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

THRESHOLD = 0.75

def get_avg_f1_score(calculate_metrics, pred_dir_name, ref_dir_name):
    scores = get_scores(calculate_metrics, pred_dir_name, ref_dir_name)
    averages = {"precision":0, "recall":0, "f1_score":0}

    for i in range(len(scores)):
        averages["precision"] += scores[i]["precision"]
        averages["recall"] += scores[i]["recall"]
        averages["f1_score"] += scores[i]["f1_score"]

    averages["precision"] = float('%.3f'%(averages["precision"] / len(scores)))
    averages["recall"] = float('%.3f'%(averages["recall"] / len(scores)))
    averages["f1_score"] = float('%.3f'%(averages["f1_score"] / len(scores)))
    
    return averages

def get_scores(calculate_metrics, pred_dir_name, ref_dir_name):
    scores = []
    
    prediction_files = os.listdir(pred_dir_name)
    reference_files = os.listdir(ref_dir_name)

    for pred_file_name in prediction_files:
        for ref_file_name in reference_files:
            if pred_file_name == ref_file_name:
                try:
                    pred_file_path = os.path.join(pred_dir_name, pred_file_name)
                    ref_file_path = os.path.join(ref_dir_name, ref_file_name)
                    with open(pred_file_path, 'r') as pred_file:
                        pred_graph = json.loads(pred_file.read())
                    with open(ref_file_path, 'r') as ref_file:
                        ref_graph = json.loads(ref_file.read())
                    curr_score = calculate_metrics(ref_graph, pred_graph)
                    # print(pred_file_name, curr_score)
                    scores.append(curr_score)
                except Exception as e:
                    print("Error: " + str(e))
                break
    return scores

def match_function(pred, ref):
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