import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained('THUDM/LongCite-glm4-9b', trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained('THUDM/LongCite-glm4-9b', torch_dtype=torch.bfloat16, trust_remote_code=True, device_map='auto')

with open("rare_engines_history.txt", "r") as f:
    context = f.readlines()
query = "Which company championed sleeve-valve engines during WWII?"
result = model.query_longcite(context, query, tokenizer=tokenizer, max_input_length=128000, max_new_tokens=102400)

print("Answer:\n{}\n".format(result['answer']))
print("Statement with citations:\n{}\n".format(
  json.dumps(result['statements_with_citations'], indent=2, ensure_ascii=False)))
print("Context (divided into sentences):\n{}\n".format(result['splited_context']))