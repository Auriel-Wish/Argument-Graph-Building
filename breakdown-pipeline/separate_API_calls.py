import config
utils_research_path = config.utils_research

# Start Time
# start_time = config.time.time()

#Get API key, essays to use and initial system prompt
gpt4_model = config.gpt4_model
client = config.client
essay_1 = config.essay_231
essay_2 = config.essay_198
essay_3 = config.essay_121



##################
#### Prompts #####
##################


#For Paragraph splitting
sp_1 = config.system_prompt_step1
#For retreiving Nodes for each paragraph
sp_2 = config.system_prompt_step2
#For Retreiving main ideas for each paragraph
sp_3 = config.system_prompt_step3
#For construncting graph with short-dist relations using main ideas + nodes for each paragraph.
sp_4 = config.step4_inital_prompt
#For long distance relations
sp_5 = config.step5_initial_prompt



#Step 1:
#separated_paragraphs = utils_research_path.split_paragraphs(utils_research_path.query_split_paragraphs(client, sp_1, essay_1))
separated_paragraphs = utils_research_path.split_paragraphs(essay_1)
print("Essay broken down")


#Step 2:
def init_node_ids(node_arrays):
    new_node_arrays = []
    i = 1
    for node_array in node_arrays:
        new_arr = []
        for node in node_array:
            new_node = {"text":node, "id":"N" + str(i)}
            new_arr.append(new_node)
            i += 1
        new_node_arrays.append(new_arr)
    return new_node_arrays

def query_create_nodes():
    results = []
    for i in range(len(separated_paragraphs)):     
        messages=[
            {"role": "system", "content": sp_2},
            {"role": "user", "content": separated_paragraphs[i]}
        ]
        output = utils_research_path.query_gpt(messages, client, gpt4_model)
        result_array = utils_research_path.strip_array(output)
        result_array = utils_research_path.ast.literal_eval(result_array)  #takes output and converts it into a list. May be bad if output is inconsistent.
        results.append(result_array)
        # print(result_array)
        #print(len(result_array))
        # print(' ')
    ret = init_node_ids(results)
    return ret


#An Nested Array of each node group for each paragraph in list format
result_node_arrays = query_create_nodes()
print("Nodes created")

# counter = 0
# for node_group in result_node_arrays:

#     print(node_group)
#     counter += len(node_group)
#     print()
# print("Total number of nodes is: ", counter)

# end_time = time.time()
# print('Total time: ', end_time - start_time)

#Step 3:
def query_main_points():
    main_points = []
    for i, node_group in enumerate(result_node_arrays):
        messages=[
            {"role": "system", "content": sp_3},
            {"role": "user", "content": "Paragraph: " + separated_paragraphs[i]},
            {"role": "user", "content": "ADUs: " + str(node_group)}
        ]
        output = utils_research_path.query_gpt(messages, client, gpt4_model)
        for node_group in result_node_arrays:
            for node in node_group:
                if node['id'] == output:
                    main_points.append(node)
                    break
    return main_points

#Array of each main idea corresponding to each paragraph
main_points = query_main_points()
print("Main points found")


#Step 4
edges = []
def short_dist_relations(main_points):
    for curr_index, node_group in enumerate(result_node_arrays):
        curr_main_point = main_points[curr_index]['text']
        for i in range(len(node_group)):
            for j in range(i + 1, len(node_group)):
                messages=[
                    {"role": "system", "content": sp_4},
                    {"role": "user", "content": 'Main point: ' + str(curr_main_point)},
                    {"role": "user", "content": 'ADU 1: ' + str(node_group[i]['text']) + '\nADU 2: ' + str(node_group[j]['text'])}
                ]
                output = utils_research_path.query_gpt(messages, client, gpt4_model)
                new_edge = output_to_edge(output, node_group, i, j)
                add_edge_if_not_exists(new_edge)

def add_edge_if_not_exists(new_edge):
    if new_edge != None:
        edge_exists = False
        for edge in edges:
            if edge['source'] == new_edge['source'] and edge['target'] == new_edge['target']:
                edge_exists = True
                print('Edge already exists: ' + str(new_edge))
        if not edge_exists:
            edges.append(new_edge)

def output_to_edge(output, node_group, i, j):
    output = utils_research_path.strip_array(output)
    output = utils_research_path.ast.literal_eval(output) 
    if 'support' in output[2].lower():
        return make_edge(output, 'support', node_group, i, j)
    elif 'attack' in output[2].lower():
        return make_edge(output, 'attack', node_group, i, j)
    else:
        return None

def make_edge(output, relation, node_group, i, j):
    if output[0] == 1:
        source = int((node_group[i]['id'])[1:]) - 1
        target = int((node_group[j]['id'])[1:]) - 1
    if output[0] == 2:
        source = int((node_group[j]['id'])[1:]) - 1
        target = int((node_group[i]['id'])[1:]) - 1
    return {'label': relation, 'source':source, 'target':target}


short_dist_relations(main_points)
print("Short distance relationships found")

# Step 5:
def long_dist_relations():
    for i in range(len(main_points)):
        for j in range(i + 1, len(main_points)):
            messages=[
                {"role": "system", "content": sp_5},
                {"role": "user", "content": 'ADU 1: ' + str(main_points[i]['text']) + '\nADU 2: ' + str(main_points[j]['text'])}
            ]
            output = utils_research_path.query_gpt(messages, client, gpt4_model)
            new_edge = output_to_edge(output, main_points, i, j)
            add_edge_if_not_exists(new_edge)
long_dist_relations()
print("Long distance relationships found")

# Put it all together and output
def compile_graph():
    nodes = []
    for node_array in result_node_arrays:
        for node in node_array:
            nodes.append(node)
    return {'nodes': nodes, 'edges': edges}

graph = utils_research_path.json.dumps(compile_graph(), indent=2)
print("Graph created")

with open("file_output.json", 'w') as file:
    file.write(graph)
