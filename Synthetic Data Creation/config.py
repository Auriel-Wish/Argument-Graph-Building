import random
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', '..')))
import utils_research

client = utils_research.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
gpt4o_mini_model = "gpt-4o-mini"

num_essays_to_generate = 1
save_folder = "Generated_Data"

generate_issue_prompt = "I will provide you with a topic. Your job is to output an issue that is at the center of some conflict of opinion about that topic. It should be an that can have multiple viewpoints and answers (i.e it should be debatable). **Only output the issue you come up with, no other text**"

generate_stance_prompt = "I will provide you with an issue that is at the center of some conflict of opinion. Your job is to output a potential stance that someone could argue regarding the topic. Do not output any reasoning for the stance. **Only output the stance iself, no other text**"

generate_essay_prompt = "I will provide you with an issue and a stance/opinion regarding the issue. Your job is to generate a 1 paragraph essay that addresses the issue and argues for the stance provided. It should be written in such a way where you make claims, and support/attack these claims with other claims. There are 3 types of claims you can use: 1) Factual - this can be observed and verified in the real world. 2) Value - this asserts the quality of someone/something, and it cannot be checked against data. 3) Policy - this says how someone or something should behave or should work. **Make sure to include all 3 types of claims**. **However, do not explicity state that you are making a claim or the type of claim you are making - those instructions are simply meant to guide you in writing the essay**. The essay paragraph must also have the following qualities:\n"

good_essay = "It must be a good essay. A good essay includes clear premises, logical conclusions, and support for an overarching claim about the given topic.\n"

bad_essay = "It must be a poorly made essay. A poorly made essay is one that appears to make sense on the surface level, but is actually incorrect. This can include things like logical fallacies, circular reasoning, and factually incorrect statements. An example of a (short) bad argument is: 'Lemons are yellow because they absorb yellow light. Moreover, the fact that lemons are yellow means that they absorb yellow light.' This has circular reasoning by saying A is true because of B AND B is true because of A, and it is factually incorrect - lemons are yellow because they reflect yellow light, not absorb it. Note that even though the argument is flawed, it still makes sense on the surface level and uses argumentative language correctly.\n"

absurd_essay = "It must be an absurd essay. An absurd essay is one that uses argumentative language correctly, but has ideas that do not make any sense. The overall claim should be completely absurd, but the essay should be **internally consistent** and stay on topic. Ensure the use of argumentative language is correct.\n"

essay_quality = [good_essay, bad_essay, absurd_essay]

essay_quality_names = ["Good", "Bad", "Absurd"]

normal_attack = ""

more_attack = "The essay must address at least one counter-argument to the stance you took."

most_attack = "The essay must address mutliple counter-arguments, along with counter-arguments to those counter-arguments (which ultimately support the stance you took). While the essay must take the given stance, it must provide a holistic perspective."

attack_relation_quantity = [normal_attack, more_attack, most_attack]

arg_topics = [
    "Should plastic be banned",
    "Pollution due to Urbanization",
    "Education should be free",
    "Should Students get limited access to the Internet",
    "Selling Tobacco should be banned",
    "Smoking in public places should be banned",
    "Facebook should be banned",
    "Students should not be allowed to play PUBG",
    "Technology",
    "Computer",
    "Wonder Of Science",
    "Mobile Phone",
    "Internet",
    "Newspaper",
    "Science",
    "Importance of Education",
    "Education should be free",
    "Contribution of Technology in Education",
    "Dog",
    "Lion",
    "Peacock",
    "Cat",
    "My Favorite Animal",
    "Leadership",
    "Swami Vivekananda",
    "Mother Teresa",
    "Rabindranath Tagore",
    "Sardar Vallabhbhai Patel",
    "Subhash Chandra Bose",
    "Abraham Lincoln",
    "Martin Luther King",
    "Rainy Season",
    "Climate Change",
    "Nature",
    "Deforestation",
    "Natural Disasters",
    "Flood",
    "Noise Pollution",
    "Patriotism",
    "Health",
    "Corruption",
    "Science and Technology",
    "Importance of Sports",
    "Music",
    "Earthquake",
    "Football",
    "Happiness",
    "Success",
    "Unemployment",
    "Junk Food",
    "Freedom",
    "Human Rights",
    "Knowledge Is Power",
    "Same Sex Marriage",
    "Cyber Crime",
    "Politics",
    "Time",
    "Yoga",
    "Tourism",
    "Unity In Diversity",
    "Artificial Intelligence",
    "Online Shopping",
    "Freedom Fighters",
    "Garden",
    "Grandparents",
    "Recycling",
    "Disaster Management",
    "Capital Punishment",
    "College Life",
    "Peer Pressure",
    "Motivation",
    "Nature Vs Nurture",
    "Importance of Family",
    "Importance of Independence Day",
    "Action Speaks Louder Than Words",
    "Demonetization",
    "Agriculture",
    "Population Explosion",
    "Poverty",
    "Cruelty To Animals",
    "Google",
    "Nelson Mandela",
    "Organ Donation",
    "Life in a Big City",
    "Ethics",
    "Chess",
    "School students should be allowed to curate their high school curriculum.",
    "The role of physical education in the school system.",
    "Should the death sentence be implemented globally?",
    "It should be illegal to use certain types of animals for experiments and other research purposes.",
    "Should the government do more to improve accessibility for people with physical disabilities?",
    "Do people learn the art of becoming a politician, or are they born with it?",
    "Social media platform owners should monitor and block comments containing hateful language.",
    "Does technology play a role in making people feel more isolated?",
    "Will there ever be a time when there will be no further technological advancements?",
    "It should be illegal to produce and sell tobacco.",
    "Girls should be motivated to take part in sports.",
    "Rape victims should abort their unborn children.",
    "Fathers should get equal paternity leave.",
    "Do teenagers get into trouble because they are bored?",
    "Individuals who have failed at parenting should be punished.",
    "Vaping is less harmful than smoking cigarettes.",
    "Covid-19 vaccination has more cons than pros.",
    "Social media is the real cause of teenage depression.",
    "Is the American education system perfect for society?",
    "Recycling should be made compulsory."
]