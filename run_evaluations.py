from inspect_ai import eval_set
from datetime import datetime

success, logs = eval_set(
   tasks=["reward_hacking_eval.py"],
   model=["openai/gpt-4.1-mini", "anthropic/claude-3-5-haiku-latest"],
   log_dir=f"logs-bulk-{datetime.now().strftime('%Y%m%d%H%M%S')}"      
)