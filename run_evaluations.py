from inspect_ai import eval_set
from datetime import datetime

success, logs = eval_set(
   tasks=["reward_hacking_eval.py"],
   model=["openai/gpt-4.1",
          "openai/gpt-5-mini",
          "openai/gpt-5",
          "anthropic/claude-3-5-haiku-latest",
          "anthropic/claude-sonnet-4-20250514",
        "anthropic/claude-opus-4-1-20250805",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash",
          ],
   log_dir=f"logs-bulk-{datetime.now().strftime('%Y%m%d%H%M%S')}"      
)