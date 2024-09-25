import dspy

class Expert(dspy.Signature):
    """Given a fragment of a conversational turn, you must decide whether or not there is a TRP opportunity available
    
    A Turn Construction Unit (TCU) describes pieces of conversation which may comprise an entire speaking turn by a speaker. A listener will look for the places where they can start speaking - so-called transition relevant places (TRPs) - based on how the units appear over time. A TRP marks a point where the turn may go to another speaker, or the present speaker may continue with another TCU.
    
    The input fragment may contain a "<START>" or "<END>" token indicating whether the fragment includes the start or end of the overall TCU. 
    """

    fragment:str = dspy.InputField(desc="contains a fragment of a conversational turn")
    response:bool = dspy.OutputField(desc="returns True if the fragment ends with a TRP opportunity and False otherwise")



class Participant(dspy.Signature):
    """
    Carefully review the input fragment from a conversational turn, and pretend you are in a conversation with the speaker who is uttering the turn. You want to encourage them to continue speaking by saying “yeah”, or “mmhmm”, or a similar single-word response. Therefore, determine if after this fragment it is an appropriate point in time to start speaking. For example, is this an appropriate time encourage the speaker to continue speaking or go on by saying a single word (e.g., “yeah”, “mmhmm”, “no” etc.).
    
    The input fragment may contain a "<START>" or "<END>" token indicating when the speaker starts speaking and when they end. If it does not contain <END> then that means the speaker has not finished speaking.

    Remember, the goal is determine if at the end of the frame it is appropriate or not to vocalize encouragement.
    """

    fragment:str = dspy.InputField(desc="contains a fragment of a conversational turn")
    response:bool = dspy.OutputField(desc="returns True if it is appropriate to start speaking and False otherwise")
