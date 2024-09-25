import json
import ast

# JSON -> text with IDs
def json_to_text_with_node_ids(json_data: dict, essay: str):
    nodes = json_data['nodes']
    edges = json_data['edges']

    for node in nodes:
        curr_id = node['id']
        curr_text = node['text']
        starting_index = essay.find(curr_text)
        ending_index = starting_index + len(curr_text)
        essay = essay[:starting_index] + "{{" + essay[starting_index:ending_index] + " || " + curr_id + "}} (())" + essay[ending_index:]

    edge_mapping = {}
    for node in nodes:
        edge_mapping[node['id']] = ([], [])
    for edge in edges:
        source = edge['source']
        target = edge['target']
        label = edge['label']
        if 'support' in label.lower():
            edge_mapping[source][0].append(target)
        elif 'attack' in label.lower():
            edge_mapping[source][1].append(target)
    
    for node_id, (supports_list, attacks_list) in edge_mapping.items():
        starting_index = essay.find("| " + node_id + "}")
        starting_index = essay.find('()', starting_index) + 1
        essay = essay[:starting_index] + "support: [" + str(supports_list) + "], attack: [" +  str(attacks_list) + "]" + essay[starting_index:]
    
    return essay

# JSON -> text with no IDs
def json_to_text_with_node_text(json_data: dict, essay: str) -> str:
    essay = json_to_text_with_node_ids(json_data, essay)
    essay = replace_ids_with_text(json_data, essay)
    return essay

def replace_ids_with_text(json_data: dict, essay: str) -> str:
    all_node_ids = []
    index_of_bar = essay.find('||')
    while index_of_bar != -1:
        index_of_curly_brace = essay.find('}', index_of_bar)
        node_id = essay[index_of_bar + 3:index_of_curly_brace]
        all_node_ids.append(node_id)
        essay = essay[:index_of_bar - 1] + essay[index_of_curly_brace:]
        index_of_bar = essay.find('||', index_of_bar + 1 - len(node_id))
    
    for node_id in all_node_ids:
        for node in json_data['nodes']:
            if node['id'] == node_id:
                essay = essay.replace(("'" + node_id + "'"), ("'''" + node['text'] + "'''"))
                break
    
    return essay

# text with IDs -> JSON
def text_with_ids_to_json(essay: str) -> dict:
    nodes = []
    edges = []
    index_of_opening_brace = essay.find('{{')
    while index_of_opening_brace != -1:
        index_of_closing_brace = essay.find('}}', index_of_opening_brace)
        if index_of_closing_brace == -1:
            break
        curr_section = essay[index_of_opening_brace + 2:index_of_closing_brace]
        index_of_bar = curr_section.find('||')
        node_text = curr_section[:index_of_bar - 1]
        node_id = curr_section[index_of_bar + 3:]
        nodes.append({'text': node_text, 'id': node_id})
        index_of_opening_brace = essay.find('{{', index_of_closing_brace)

        index_of_opening_parenthesis = essay.find('((', index_of_closing_brace)
        index_of_closing_parenthesis = essay.find('))', index_of_opening_parenthesis)
        curr_section = essay[index_of_opening_parenthesis + 2:index_of_closing_parenthesis]
        index_of_opening_bracket = curr_section.find('[[')
        index_of_closing_bracket = curr_section.find(']]')
        # print(curr_section[index_of_opening_bracket + 2:index_of_closing_bracket])
        supports_list = [node_id.strip()[1:len(node_id.strip()) - 1] for node_id in curr_section[index_of_opening_bracket + 2:index_of_closing_bracket].split(',') if node_id != ""]
        index_of_opening_bracket = curr_section.find('[[', index_of_closing_bracket)
        index_of_closing_bracket = curr_section.find(']]', index_of_opening_bracket)
        attacks_list = [node_id.strip()[1:len(node_id.strip()) - 1] for node_id in curr_section[index_of_opening_bracket + 2:index_of_closing_bracket].split(',') if node_id != ""]

        for support in supports_list:
                edges.append({'label': 'support', 'source': node_id, 'target': support})
        for attack in attacks_list:
                edges.append({'label': 'attack', 'source': node_id, 'target': attack})
    
    return {'nodes': nodes, 'edges': edges}

# text with no IDs -> JSON
def text_without_ids_to_json(essay: str) -> dict:
    nodes = []
    edges = []

    node_dict = {}
    
    index_of_starting_brace = essay.find('{{')
    index_of_closing_brace = essay.find('}}')
    counter = 0
    while index_of_starting_brace != -1:
        counter += 1
        node_id = "N" + str(counter)
        node_text = essay[index_of_starting_brace + 2:index_of_closing_brace]
        nodes.append({"text": node_text, "id": node_id})
        node_dict[node_text] = node_id
        index_of_starting_brace = essay.find('{{', index_of_closing_brace)
        index_of_closing_brace = essay.find('}}', index_of_starting_brace)
    
    index_of_starting_paren = essay.find('(support: [[')
    index_of_closing_paren = essay.find(']]))', index_of_starting_paren) + 1
    counter = 0
    while index_of_starting_paren != -1:
        counter += 1
        node_id = "N" + str(counter)

        start_of_array = essay.find('[[', index_of_starting_paren) + 1
        end_of_array = essay.find(']]', start_of_array) + 1
        supports_array = ast.literal_eval(essay[start_of_array:end_of_array])

        start_of_array = essay.find('[[', end_of_array) + 1
        end_of_array = essay.find(']]', start_of_array) + 1
        attacks_array = ast.literal_eval(essay[start_of_array:end_of_array])

        for support_text in supports_array:
            edges.append({"label": "support", "source": node_id, "target": node_dict[support_text]})
        for attack_text in attacks_array:
            edges.append({"label": "attack", "source": node_id, "target": node_dict[attack_text]})

        index_of_starting_paren = essay.find('(support: [[', index_of_closing_paren)
        index_of_closing_paren = essay.find(']]))', index_of_starting_paren) + 1
    
    return {"nodes": nodes, "edges": edges}