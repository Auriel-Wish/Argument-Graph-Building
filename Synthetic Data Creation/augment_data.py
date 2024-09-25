import os
from config import *
import sys
sys.path.append(os.path.join(os.getcwd(), "..", 'utility_scripts'))
from graph_validity import is_valid_graph # type: ignore

client = utils_research.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

json_dir = 'Annotated_Data/JSON'
text_dir = 'Annotated_Data/Raw-Text'
augmented_dir = 'Augmented_Data'

def query_gpt(messages, client, model, temp):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp
    )
    return completion.choices[0].message.content

augment_prompt_part1 = '''
You will be given an argumentative essay along with a JSON graph where the nodes
are argumentative discourse units (ADUs). Your goal is to modify text in the essay
and the corresponding text in the nodes according to the following strategy:\n
'''

augment_prompt_part2 = '''
DO NOT CHANGE ANY EDGES, THE NUMBER OF NODES, OR THE MEANING OF TEXT IN THE NODES.
Only change the way in which the text in a given node is written.
Any text you edit in the essay should be reflected in the corresponding node text.
Output the edited essay and the edited JSON graph in the following format:
ESSAY: <edited essay>
GRAPH: <edited JSON graph>
'''

augment_strategies = [
    '''Rewrite the essay and nodes to make them sound like it is written by someone who speaks English as a second or third language, lacking language familiarity, fluency, having alternative word choices, having different degrees of politeness, and deference.''',
    '''Rewrite the essay and nodes by changing the verbs and nouns with synonyms or other ways of describing the same action or object.''',
    '''Rewrite the essay and nodes to make them more indirect and polite.''',
    '''Rewrite the essay and nodes to make them more direct and impolite.''',
    '''Rewrite the essay and nodes to make them more formal.''',
    '''Rewrite the essay and nodes to make them less formal and much more casual, almost like something someone might say on twitter or reddit.''',
    '''Rewrite the essay and nodes to make them more verbose.''',
    '''Rewrite the essay and nodes to make them more concise.''',
]

def augment_data():
    for file_name in os.listdir(json_dir):
        if file_name.endswith('.json') and not os.path.exists(os.path.join(augmented_dir, file_name)):
            json_file_path = os.path.join(json_dir, file_name)
            text_file_path = os.path.join(text_dir, os.path.splitext(file_name)[0] + '.txt')
            
            with open(json_file_path, 'r') as json_file, open(text_file_path, 'r') as text_file:
                graph = json_file.read()
                essay = text_file.read()

                augmented_file_path = os.path.join(augmented_dir, file_name)
                with open(augmented_file_path, 'w') as f:
                    f.write(json.dumps([]))

                for strategy in augment_strategies:
                    messages = [
                        {"role": "system","content": augment_prompt_part1},
                        {"role": "user","content": strategy},
                        {"role": "system","content": augment_prompt_part2},
                        {"role": "user","content": essay},
                        {"role": "user","content": graph}
                    ]
                    for i in range(15):
                        temp = 0.2
                        generate_new_data(temp, messages, client, gpt4o_mini_model, file_name, strategy, i, augmented_file_path)
                    for i in range(15):
                        temp = 0.8
                        generate_new_data(temp, messages, client, gpt4o_mini_model, file_name, strategy, i, augmented_file_path)

def generate_new_data(temp, messages, client, gpt4o_mini_model, file_name, strategy, i, augmented_file_path):
    print(f"file: {file_name}, strategy: {strategy}, temperature: {temp}, iteration: {i}")
    response = query_gpt(messages, client, gpt4o_mini_model, temp)
    start_index = response.find('ESSAY: ') + len('ESSAY: ')
    end_index = response.rfind('GRAPH: ')
    new_edited_essay = response[start_index:end_index].strip()
    start_index = response.find('{', end_index)
    end_index = response.rfind('}') + 1
    new_edited_graph = json.loads(response[start_index:end_index].strip())
    output = {
        "strategy": strategy,
        "temperature": temp,
        "iteration": i,
        "edited_essay": new_edited_essay,
        "edited_graph": new_edited_graph
    }

    data = []
    with open(augmented_file_path, 'r') as f:
        data = json.load(f)
        data.append(output)
    with open(augmented_file_path, 'w') as f:
        f.write(json.dumps(data, indent=2))
    

def validate_graphs():
    valid = 0
    invalid = 0
    for file_name in os.listdir(augmented_dir):
        if not file_name.endswith('.json'):
            continue
        all_versions = []
        curr_json = json.load(open(os.path.join(augmented_dir, file_name), 'r'))
        original_graph = json.load(open(os.path.join(json_dir, file_name), 'r'))
        
        for version in curr_json:
            try:
                new_graph = version["edited_graph"]
                version["is_valid_graph"] = is_valid_graph(new_graph)
                version["has_same_edges"] = (new_graph["edges"] == original_graph["edges"])
                old_nodeset = set([node["id"] for node in original_graph["nodes"]])
                new_nodeset = set([node["id"] for node in new_graph["nodes"]])
                version["different_node_ids"] = list(old_nodeset.symmetric_difference(new_nodeset))
                if version["is_valid_graph"] and version["has_same_edges"] and len(version["different_node_ids"]) == 0:
                    valid += 1
                    all_versions.append(version)
                else:
                    invalid += 1
            except:
                invalid += 1

        with open(os.path.join(augmented_dir, file_name), 'w') as f:
            f.write(json.dumps(all_versions, indent=2))
    
    print(f"Valid: {valid}, Invalid: {invalid}")

# augment_data()
validate_graphs()