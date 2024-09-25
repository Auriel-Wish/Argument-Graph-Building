import dspy
from graph_generation_signature import GenerateGraph, GenerateAnnotations
import os
import json
import sys
from f1_score_metrics import annotations_output_metric, graph_output_metric
from dspy.teleprompt import *
from zero_shot import ZeroShotModule
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'datasets', 'utility_scripts')))
from text_to_json_and_back_scripts import * # type: ignore


essay = '''
Martin Luther King Jr.'s legacy, deservedly celebrated, should focus more on his achievements in civil rights because these accomplishments fundamentally redefined the societal landscape of the United States. King's leadership in the Civil Rights Movement dismantled legal segregation and broke down numerous barriers of racial discrimination. The Civil Rights Act of 1964 and the Voting Rights Act of 1965 are monumental testimonies to his relentless struggle for equality and justice for African Americans. By focusing on these pivotal achievements, we highlight the systemic changes that have had lasting impacts on American society, promoting a more inclusive and just environment for future generations.

Focusing on King's civil rights achievements also serves to honor the substantial sacrifices made by countless individuals who fought alongside him. These efforts were built on the foundation of his vision for racial equality and showcased his ability to galvanize a diverse coalition of supporters. King's civil rights work, amplified through seminal events like the March on Washington, where he delivered his iconic "I Have a Dream" speech, remains a powerful testament to his profound impact on American history. Highlighting these milestones underscores the significance of his leadership in overcoming deeply entrenched racial prejudices and injustices.

Moreover, emphasizing King's civil rights accomplishments aligns with the ongoing struggle for racial equality in contemporary society. Despite the advances made, systemic racism continues to threaten social justice. By focusing on King's civil rights achievements, we reinforce the importance of continued vigilance against racial discrimination. This focus does not preclude the recognition of his broader social and economic initiatives, but it ensures that the core of his legacy remains grounded in the profound, transformative changes he effected within the realm of civil rights. By celebrating and learning from these triumphs, future generations can be inspired to continue his work toward achieving true racial equality.
'''

# essay = '''
# Martin Luther King Jr.'s legacy, deservedly celebrated, should focus more on his achievements in civil rights because these accomplishments fundamentally redefined the societal landscape of the United States. King's leadership in the Civil Rights Movement dismantled legal segregation and broke down numerous barriers of racial discrimination. The Civil Rights Act of 1964 and the Voting Rights Act of 1965 are monumental testimonies to his relentless struggle for equality and justice for African Americans. By focusing on these pivotal achievements, we highlight the systemic changes that have had lasting impacts on American society, promoting a more inclusive and just environment for future generations.
# '''

def get_examples():
    json_dir = '../datasets/Synthetic/Annotated_Data/JSON'
    text_dir = '../datasets/Synthetic/Annotated_Data/Raw-Text'

    json_files = [os.path.join(json_dir, file) for file in os.listdir(json_dir) if file.endswith('.json')]

    examples = []
    for i, json_file in enumerate(json_files):
        text_file = os.path.join(text_dir, os.path.basename(json_file).replace('.json', '.txt'))
        if os.path.exists(text_file):
            with open(json_file, 'r') as f_json, open(text_file, 'r') as f_text:
                essay = f_text.read()
                json_data = json.load(f_json)
                text_with_node_ids = json_to_text_with_node_ids(json_data, essay) # type: ignore
                # examples.append(dspy.Example(essay=essay, graph=json_data).with_inputs("essay"))
                examples.append(dspy.Example(essay=essay, annotated_essay=text_with_node_ids).with_inputs("essay"))
        if i > 10:
            break
    return examples

def create_graph():
    trainset = get_examples()

    gpt_4o_mini = dspy.OpenAI(model="gpt-4o-mini", api_key=os.environ.get('OPENAI_API_KEY'), api_provider = "openai", model_type="chat")
    dspy.configure(lm=gpt_4o_mini, max_tokens=4096)
    
    # zero_shot = ZeroShotModule(signature=GenerateAnnotations)
    # result = zero_shot(essay=essay)
    # graph = text_with_ids_to_json(result.annotated_essay) # type: ignore
    # print("V1\n", result.annotated_essay)
    # print(json.dumps(graph, indent=2)) 

    # config = dict(max_bootstrapped_demos=4, max_labeled_demos=4, num_candidate_programs=10, num_threads=4)
    # teleprompter = BootstrapFewShotWithRandomSearch(metric=annotations_output_metric, **config)
    # teleprompter = BootstrapFewShotWithRandomSearch(metric=annotations_output_metric)
    teleprompter = BootstrapFewShot(metric=annotations_output_metric, teacher_settings=dict({'lm': gpt_4o_mini}))

    optimized_program = teleprompter.compile(student=ZeroShotModule(signature=GenerateAnnotations), trainset=trainset)

    optimized_program.save('optimized_program.json')

create_graph()
    
# generate_graph = dspy.ChainOfThought(GenerateGraph, max_tokens=4096)
# response = generate_graph(essay=essay)

# print(response.graph)
# print(response.rationale)