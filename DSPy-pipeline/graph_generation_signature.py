import dspy
from graph_type import GraphModel

class GenerateGraph(dspy.Signature):
    """
    Create a graph from the given essay where nodes are argumentative discourse
    units (ADUs) and edges are the support/attack relations between the nodes.

    The graph is a JSON object with the following structure:
    {
        "nodes": [
            {
                "id": "N#",
                "text": "node text",
                "type": "fact" OR "policy" OR "value"
            },
            ...
        ],
        "edges": [
            {
                "source": "N#",
                "target": "N#",
                "type": "support" OR "attack"
            },
            ...
        ]
    }

    Output only the JSON, nothing else, not even the words ```JSON
    """

    essay:str = dspy.InputField(description="The essay to generate the graph from.")
    graph:str = dspy.OutputField(description="The generated JSON graph.")

class GenerateAnnotations(dspy.Signature):
    """
    Annotate the given essay by breaking up the essay into argumentative
    discourse units (ADUs) and identifying the support/attack relations between
    them. 

    The format should be: non-ADU text... {{node text || N#}} ((support: [[]] attack: [[N#, N#, ...]])) non-ADU text...
    non-ADU text is text in the essay that is not argumentative. ADU text is the
    text of the ADU. N# is the node number of the ADU.
    """

    essay:str = dspy.InputField(description="The essay to generate the graph from.")
    annotated_essay:str = dspy.OutputField(description="The annotated essay.")