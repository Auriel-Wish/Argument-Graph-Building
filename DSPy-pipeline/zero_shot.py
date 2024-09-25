import dspy

class ZeroShotModule(dspy.Module):
    """ 
    Basic module
    """
    def __init__(self, signature:dspy.Signature):
        super().__init__()
        self.CoT = dspy.ChainOfThought(signature, max_tokens=4096) 
    
    def forward(self, essay:str):
        try:
            response = self.CoT(essay=essay)
            return response
        except Exception as e:
            print(f"LLM call failed with error: {e}")
            return self.CoT(essay=None)
