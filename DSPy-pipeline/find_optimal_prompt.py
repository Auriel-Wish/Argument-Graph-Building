from sklearn.model_selection import train_test_split
import dspy
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'datasets', 'utility_scripts')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'evaluation')))
from text_to_json_and_back_scripts import * # type: ignore
from Node_f1_score_v2 import calculate_metrics as calc_node_metrics # type: ignore
from Edge_f1_score_v2 import calculate_metrics as calc_edge_metrics # type: ignore

def optimize_prompt():
    initial_prompt = '''
    You are given a argumentative essay. Your task is to analyze the logical structure of the essay and annotate it using a specified format. The goal is to identify and label distinct segments of text, referred to as "nodes," which represent individual claims, statements, or arguments. Each node should be assigned a unique identifier (e.g., N1, N2, etc.).

    For each node, determine its relationship with other nodes in the essay. Specifically, you should identify whether the node supports or attacks other nodes. If a node supports another node, it provides evidence or reasoning that strengthens the other node's argument. If a node attacks another node, it challenges or weakens the other node's argument.

    Task Details:

    1. **Identify Key Segments:** 
    - Break down the essay into meaningful segments, where each segment expresses a distinct idea, argument, or point.
    - Assign a unique node ID to each segment (e.g., N1, N2, etc.).

    2. **Determine Relationships:**
    - Analyze the relationships between these segments. For each segment (node), decide whether it **supports** or **attacks** any other segment (node).
    - For example, if one segment provides evidence or justification for another, it should be marked as supporting it. If a segment contradicts or challenges another, it should be marked as attacking it.
    - A node can support or attack multiple nodes, and vice versa.

    3. **Annotation Format:**
    - Annotate each segment using the following format: 
        - {{text segment || N#}} ((support: [['N#', 'N#', ...]], attack: [['N#', 'N#', ...]])).
    - Replace N# with the actual node IDs.
    - If a node supports or attacks another node, list the relevant node IDs in the support or attack fields. If a node neither supports nor attacks, leave the list empty.

    Only output the annotated essay itself.
    '''

    data = get_data()
    train_essays, val_essays = train_test_split(data, test_size=0.2, random_state=42)

    teacher = dspy.OpenAI(model="gpt-4o-mini", api_key=os.environ.get('OPENAI_API_KEY'), api_provider = "openai", model_type="chat")
    config = dict(max_bootstrapped_demos=4, max_labeled_demos=4, num_candidate_programs=10, num_threads=4)
    teleprompter = BootstrapFewShotWithRandomSearch(metric=custom_f1_metric, **config, teacher_settings=dict({'lm': teacher}))
    optimized_program = teleprompter.compile(student=teacher, trainset=train_essays, valset=val_essays)
    optimized_program.save("optimized_program")

def custom_f1_metric(predictions, reference):
    pred_graph = text_with_ids_to_json(predictions) # type: ignore
    ref_graph = text_with_ids_to_json(reference) # type: ignore

    node_f1_score = calc_node_metrics(ref_graph, pred_graph)['f1_score']
    edge_f1_score = calc_edge_metrics(ref_graph, pred_graph)['f1_score']

    return 0.25 * node_f1_score + 0.75 * edge_f1_score

def get_data():
    json_dir = '../datasets/Synthetic/Annotated_Data/JSON'
    text_dir = '../datasets/Synthetic/Annotated_Data/Raw-Text'

    json_files = [os.path.join(json_dir, file) for file in os.listdir(json_dir) if file.endswith('.json')]

    data = []
    for json_file in json_files:
        text_file = os.path.join(text_dir, os.path.basename(json_file).replace('.json', '.txt'))
        if os.path.exists(text_file):
            with open(json_file, 'r') as f_json, open(text_file, 'r') as f_text:
                essay = f_text.read()
                json_data = json.load(f_json)
                text_with_node_ids = json_to_text_with_node_ids(json_data, essay) # type: ignore
                data.append({"essay": essay, "annotations": text_with_node_ids})
    return data

optimize_prompt()
