import config
utils_research_path = config.utils_research


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
sp_4 = config.step4_inital_prompt_single_API_call
#For long distance relations
sp_5 = config.step5_initial_prompt

graph = {"nodes":[], "edges":[]}

# Split essay into paragraphs
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
    ret = init_node_ids(results)
    return ret


#An Nested Array of each node group for each paragraph in list format
result_node_arrays = query_create_nodes()
print("Nodes created")

def add_nodes_to_graph():
    for node_array in result_node_arrays:
        for node in node_array:
            graph["nodes"].append(node)
add_nodes_to_graph()


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
def short_dist_relations():
    for curr_index, node_group in enumerate(result_node_arrays):
        # Overall message prompt to be sent to GPT
        messages = [
            {"role": "system", "content": sp_4},
            {"role": "user", "content": separated_paragraphs[curr_index]}
        ]
        for i in range(len(node_group)):
            for j in range(i + 1, len(node_group)):
                messages.append(
                    {"role": "user", "content": str(node_group[i]) + '\n' + str(node_group[j])}
                )
        output = utils_research_path.strip_array(utils_research_path.query_gpt(messages, client, gpt4_model))
        output = utils_research_path.ast.literal_eval(output)
        add_edges_to_graph(output)
        # new_edge = output_to_edge(output, node_group, i, j)
        # add_edge_if_not_exists(new_edge)

def add_edges_to_graph(edge_list):
    for edge in edge_list:
        if 'support' in edge[2].lower():
            graph["edges"].append({"label":"support", "source": int(edge[0][1:]) - 1, "target":int(edge[1][1:]) - 1})
        elif 'attack' in edge[2].lower():
            graph["edges"].append({"label":"attack", "source": int(edge[0][1:]) - 1, "target":int(edge[1][1:]) - 1})

short_dist_relations()
print("Short distance relationships found")

# # Step 5:
def long_dist_relations():
    messages = [
        {"role": "system", "content": sp_5},
        {"role": "user", "content": "Essay: " + essay_1}
    ]
    for i in range(len(main_points)):
        for j in range(i + 1, len(main_points)):
            messages.append(
                {"role": "user", "content": str(main_points[i]) + '\n' + str(main_points[j])}
            )
    output = utils_research_path.ast.literal_eval(utils_research_path.strip_array(utils_research_path.query_gpt(messages, client, gpt4_model)))
    add_edges_to_graph(output)

long_dist_relations()
print("Long distance relationships found")

with open("graph.json", 'w') as file:
    file.write(utils_research_path.json.dumps(graph, indent=2))
print("Graph created")