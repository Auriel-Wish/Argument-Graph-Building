import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
import utils_research

#API access key
client = utils_research.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

#current OpenAI model we are using.
gpt4_model = "gpt-4o"


#Essay for testing
essay_231 = '''
It's certainly better for children to grow up in a big city. Of course you need to choose a good neighborhood. I hold this belief because of two main reasons, academic and social reasons.
Some people thinks that if a child grows up in a big city they will be all day at home at the computer or at the video-game, but this is not true if you live in a neighborhood with other people about your age as I did. My friends and I used to play soccer, bike, climb trees and do a lot of other stuff every day. We did play video-games, but that wasn't our main activity. In a big city there are more kinds of people and more things to do.
I have a friend that grew up in the countryside. He said that he had to study a lot to pass the test to enter the university. This is another downside of growing up in the countryside. In a big city you have more qualified teachers and a better access to technology.

Growing up in the countryside is not such a good experience, you won't know a lot of people, there are gossips everywhere, and your life will be really limited. If someday I have children, I'm absolutely sure that they will grow up in a good neighborhood of a big city and they will be very happy about it.

'''

#Essay for testing
essay_198 = '''
Working longer hours is becoming prevalent in these days. There is a saying in my native village, "Health is Wealth". I believe many of people including me are not really considering the importance of health. The need for increased working hours might be because of enhanced competitive environment and desire to acquire much money and promotion. However, people working for extended hours have been found having adverse effects on their health and personal life. In my opinion, a balance between personal and professional life should be created by restricting maximum number of working hours. 
First of all, many of us would agree to the fact that people; who prefer working longer hours, do not find time to focus on their health. By working too long, they often become tired, lazy and reluctant to carry out physical exercise in order to remain fit and healthy and eventually loose health and become sick. Moreover, they become extensively addicted to their work and become workaholic type persons. The repercussion are so severe that their families and friends remain deprived off their attention and in the end they end up losing balance between their family and personal life.
Secondly, these workaholic people do not spend time for the contribution of society by actively participating in any social campaign. As they usually remain busy in their office so they do not find leisure time for such social activities. For instance, I would take my boss's example; he has been working for extended hours in office for many years. Recently, his health and personal life was drastically affected as he broke up with his wife and his family life has totally been in chaos and cries. He started regretting afterwards and now trying to manage his work but it seems to be too late for him.
To conclude this, I would strongly emphasis and recommend, Government must include the clause of maximum number of working hours in its Labor Law and enforce to all companies for ensuring their employees do not spend extended hours in companies. This will help in uplift of society, and bring the lost equilibrium between personal and professional life of each individual person.

'''



essay_121 = '''

There is no doubt that companies, factories and businesses establish to provide products which are people's need and make a profit for their managers. However, I completely disagree with the idea that businesses should be allowed to do anything they want to make a profit. With this permission they are allowed to hit and damage everything for just making a profit.
Firstly, if there is not any control on the businesses and they are permitted to do everything they want, they will threaten the beings' life such as human, animals and plants. As every day we read and hear in televisions and newspapers that some factories hit the environment by their toxic substances.
Moreover, if we let them do anything they can to just make a profit, they will produce products with low qualities and high prices, therefore they might hit consumer's life. For instance, a few months ago it was broadcast from TV that a company which produced baby milk, sold milk which did not have quality and it caused a few babies die.
In conclusion, all companies, factories and businesses should be monitored by governments and executive, and they do not have to let do anything they want just due to making profit. They can hit both the environment and human's life easily.




'''

#Intial Prompt for Splitting paragraphs
system_prompt_step1 = '''
I will give some text. Find each paragraph in it and return the string result. 
Do not modify any part of the text I give you, keep it the same. Just split
into the relevant paragraphs based on reading it, identifying the key ideas,
looking for transitions and formatting cues.

So if the output I give you for example is a big piece of text that
is 4 paragraphs, your result will be that same text, unmodified
but just split into the 4 distinct paragraphs.

If you see just/detect one paragraph in the given text, then just return that whole text as is. 

Space the output such that there is one newline between each paragraph
'''


system_prompt_step2 = '''
I will give you a piece of argumentative text. I want you to break up the text into argumentative discourse units (ADU) such that each ADU is an entry in a python array.
An ADU is a section of text (usually a sentence or part of a sentence) that serves either as a proposition (asserting something) or as evidence (supporting or attacking another ADU).
You are not specifically splitting up ADUs based on punctuation. ADUs should be split based on when its idea starts and ends.


Output only the array of ADUs.
'''



system_prompt_step3 = '''
You will receive a list of nodes where each node is an argumentative discourse unit.
You will also receive the paragraph associated with the list.
Pick which node captures the main idea of the paragraph and
return its associated id.

Output only the id of the node.
'''



system_prompt_step4 = '''

Task: Identify relations between Argument Discourse Units.
Background: You will receive an array of ADUs representing an argumentative text, along with the main idea of the text to provide a broader context for the given text and to help you predict more accurate relations.

Example:

Input 1:
["I hold this belief because of two main reasons, academic and social reasons", 
"You won't know a lot of people, there are gossips everywhere, and your life will be really limited", 
"Growing up in the countryside is not such a good experience"]

Input 2: Main Idea-> Children benefit more from growing up in a big city due to better academic and social opportunities, although it's important to choose a good neighborhood.

Output:
{
    "nodes": [
        {"text": "I hold this belief because of two main reasons, academic and social reasons", "id": "N1"},
        {"text": "You won't know a lot of people, there are gossips everywhere, and your life will be really limited", "id": "N2"},
        {"text": "Growing up in the countryside is not such a good experience", "id": "N3"}
    ],
    "edges": [
        {"source": 1, "target": 2, "label": "support"}
    ]
}

Instructions:
1. Examine the given ADUs and determine which ADUs have a SUPPORTS or ATTACKS with any other ADUs. If a given ADU does not support or attack any other ADU, that is ok - do not put any relation for that case.
Remember to take into account the provided main idea when determining these relationships
2. Construct a graph in JSON format with two fields: "nodes" and "edges".
   - Nodes will have two attributes: a section of the input text and a node ID. Each node should correspond to a single argumentative discourse unit (ADU) from the input text.
   - Edges will have three attributes: a label which is either "support" or "attack" (this is based on your work in step 1), a source node number, and a target node number. The text in the source node should either argumentatively support or attack the text in the target node.
3. Use 0-indexing for source and target in edges.

Input:
[
  ["Text 1 in paragraph 1", "Text 2 in paragraph 1", "Text 3 in paragraph 1"],
  ["Text 1 in paragraph 2", "Text 2 in paragraph 2"]
]

Output:
{
    "nodes": [
        {"text": "Text 1 in paragraph 1", "id": "N1"},
        {"text": "Text 2 in paragraph 1", "id": "N2"},
        {"text": "Text 3 in paragraph 1", "id": "N3"}
    ],
    "edges": [
        {"source": X, "target": Y, "label": "support/attack"}
    ]
}
{
    "nodes": [
        {"text": "Text 1 in paragraph 2", "id": "N1"},
        {"text": "Text 2 in paragraph 2", "id": "N2"}
    ],
    "edges": [
        {"source": X, "target": Y, "label": "support/attack"}
    ]
}

THERE SHOULD BE NO OTHER OUTPUT/TEXT/ besdies the JSON FILE OUTPUT WITH THE NODES AND THE EDGES SPECIFYING THE RELATIONS

'''



step4_inital_prompt = '''
You will receive a sentence discussing the main idea of a
paragraph. You will also receive 2 argumentative discourse
units. Your job is to determine the argumentative relationship between the ADUs
given the context of the main idea.
There are 3 options for a relation: **Support, Attack, No Relation**.
These relations are determined based on what the author seems to think.
If ADU 1 appears to be the reason for ADU 2
or ADU 1 appears to make ADU 2 more truthful, then ADU 1 supports ADU 2 
(and vice versa for attack).
Example 1: if ADU 2 supports ADU 1, output [2, 1, 'support'].
Example 2: if the ADUs are unrelated, output [-1, -1, 'no relation'].
Example 3: if ADU 1 attacks ADU 2, output [1, 2, 'attack'].
'''

step4_inital_prompt_single_API_call = '''
You will receive a paragraph and a list of pairs of argumentative discourse
units from that paragraph. Your job is to determine the argumentative
relationship between the pairs of ADUs given the context of the paragraph.
There are 3 options for a relation: **Support, Attack, No Relation**.
These relations are determined based on what the author seems to think.
If the essay is written in a way where ADU 1 appears to be the reason for ADU 2
or ADU 1 appears to make ADU 2 more truthful, then ADU 1 supports ADU 2 
(and vice versa for attack).
When determining the relationship between a pair of ADUs,
only consider those ADUs and the paragraph as a whole - 
do not consider any other ADU relations.
When you compare a given ADU 1 to a given ADU 2, you must also decide the
direction of the relation - **do not assume that ADU 1 supports/attacks ADU 2
just because it came first. ADU 2 may be the one supporting/attacking ADU 1**.
Output a python list of lists,
where each element in the list is a list containing 3 items - [source node, target node, relation].
Example: if N3 supports N5, N6 is unrelated to N2, and N15 attacks N2, output [['N3', 'N5', 'support'], ['N6', 'N2', 'no relation'], ['N15', 'N2', 'attack']]
**Only output this list of lists**
'''

step5_initial_prompt = '''
You will receive an essay and a list of pairs of argumentative discourse
units from that essay. Your job is to determine the argumentative
relationship between the pairs of ADUs given the context of the essay.
There are 3 options for a relation: **Support, Attack, No Relation**.
These relations are determined based on what the author seems to think.
If the essay is written in a way where ADU 1 appears to be the reason for ADU 2
or ADU 1 appears to make ADU 2 more truthful, then ADU 1 supports ADU 2 
(and vice versa for attack).
When determining the relationship between a pair of ADUs,
only consider those ADUs and the essay as a whole - 
do not consider any other ADU relations.
When you compare a given ADU 1 to a given ADU 2, you must also decide the
direction of the relation - **do not assume that ADU 1 supports/attacks ADU 2
just because it came first. ADU 2 may be the one supporting/attacking ADU 1**.
Output a python list of lists,
where each element in the list is a list containing 3 items - [source node, target node, relation].
Example: if N3 supports N5, N6 is unrelated to N2, and N15 attacks N2, output [['N3', 'N5', 'support'], ['N6', 'N2', 'no relation'], ['N15', 'N2', 'attack']]
**Only output this list of lists**
'''