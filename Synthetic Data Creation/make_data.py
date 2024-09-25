import config
utils_research_path = config.utils_research

client = config.client

arg_topics = config.arg_topics

gpt4_model = config.gpt4o_mini_model

config.random.shuffle(arg_topics)

def generate_issue(topic):
    messages=[
        {"role": "system", "content": config.generate_issue_prompt},
        {"role": "user", "content": "The topic for the issue you must generate is: " + topic}
    ]
    return utils_research_path.query_gpt(messages, client, gpt4_model)

def generate_stance(issue):
    messages=[
        {"role": "system", "content": config.generate_stance_prompt},
        {"role": "user", "content": "The issue for the stance you must generate is: " + issue}
    ]
    return utils_research_path.query_gpt(messages, client, gpt4_model)

def generate_essay(essay_prompt, issue, stance):
    messages=[
        {"role": "system", "content": essay_prompt},
        {"role": "user", "content": "The issue you are addressing is: " + issue},
        {"role": "user", "content": "The stance you must argue is: " + stance}
    ]
    return utils_research_path.query_gpt(messages, client, gpt4_model)

def run():
    for i in range(config.num_essays_to_generate):
        json_out_file = config.os.path.join(config.save_folder, "JSON", str(i + 1) + '.json')
        text_out_file = config.os.path.join(config.save_folder, "Raw-Text", str(i + 1) + '.txt')
        # json_out_file = str(i + 1) + '.json'
        # text_out_file = str(i + 1) + '.txt'
        if not config.os.path.isfile(json_out_file):
            essay_type = config.random.randint(0, len(config.essay_quality) - 1)
            attack_type = config.random.randint(0, len(config.attack_relation_quantity) - 1)
            
            topic = arg_topics[i]
            issue = generate_issue(topic)
            stance = generate_stance(issue)
            essay_prompt = config.generate_essay_prompt + config.essay_quality[essay_type] + config.attack_relation_quantity[attack_type]
            essay = generate_essay(essay_prompt, issue, stance)
            curr_json = {"topic": topic, "issue": issue, "stance": stance, "essay": essay, "quality":config.essay_quality_names[essay_type], "graph":{}}
            with open(json_out_file, 'w') as f:
                f.write(config.json.dumps(curr_json, indent=2))
            with open(text_out_file, 'w') as f:
                f.write(essay)
        print(str(i + 1))

run()