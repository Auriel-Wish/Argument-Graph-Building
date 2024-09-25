from openai import OpenAI
import config
import os
from text_to_json_and_back_scripts import text_with_ids_to_json
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def main(essay):
    messages=[
        {"role": "system", "content": "Analyze the logical structure of the given essay. Identify and label distinct ADU segments as nodes (e.g., N1, N2). Determine the relationships between these nodes, marking whether a node supports or attacks others. Use the format: {{text segment || N#}} ((support: [['N#']], attack: [['N#']]))."},
        {"role": "user", "content": essay}
    ]
    completion = client.chat.completions.create(
        model=config.model,
        messages=messages
    )
    annotated_essay = completion.choices[0].message.content
    try:
        graph = text_with_ids_to_json(annotated_essay)
        return graph
    except:
        return {"Nodes":[],"Edges":[]}