import dspy
from graph_generation_signature import GenerateGraph, GenerateAnnotations
from zero_shot import ZeroShotModule

essay = '''
Martin Luther King Jr.'s legacy, deservedly celebrated, should focus more on his achievements in civil rights because these accomplishments fundamentally redefined the societal landscape of the United States. King's leadership in the Civil Rights Movement dismantled legal segregation and broke down numerous barriers of racial discrimination. The Civil Rights Act of 1964 and the Voting Rights Act of 1965 are monumental testimonies to his relentless struggle for equality and justice for African Americans. By focusing on these pivotal achievements, we highlight the systemic changes that have had lasting impacts on American society, promoting a more inclusive and just environment for future generations.

Focusing on King's civil rights achievements also serves to honor the substantial sacrifices made by countless individuals who fought alongside him. These efforts were built on the foundation of his vision for racial equality and showcased his ability to galvanize a diverse coalition of supporters. King's civil rights work, amplified through seminal events like the March on Washington, where he delivered his iconic "I Have a Dream" speech, remains a powerful testament to his profound impact on American history. Highlighting these milestones underscores the significance of his leadership in overcoming deeply entrenched racial prejudices and injustices.

Moreover, emphasizing King's civil rights accomplishments aligns with the ongoing struggle for racial equality in contemporary society. Despite the advances made, systemic racism continues to threaten social justice. By focusing on King's civil rights achievements, we reinforce the importance of continued vigilance against racial discrimination. This focus does not preclude the recognition of his broader social and economic initiatives, but it ensures that the core of his legacy remains grounded in the profound, transformative changes he effected within the realm of civil rights. By celebrating and learning from these triumphs, future generations can be inspired to continue his work toward achieving true racial equality.
'''

optimized_program = ZeroShotModule(signature=GenerateAnnotations)
optimized_program.load('optimized_program.json')
response = optimized_program(essay=essay)
print(response.annotated_essay)