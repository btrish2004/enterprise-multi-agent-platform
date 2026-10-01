import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


class LocalLLM:
    """
    Local Qwen language model used by the planning layer.
    """

    def __init__(self):
        self.tokenizer = None
        self.model = None

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    def _load_model(self):
        """
        Load the model lazily on first use.
        """

        if self.model is not None:
            return

        print(f"Loading local LLM: {MODEL_NAME}")
        print(f"Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

        print("Local LLM loaded successfully.")

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the local Qwen model.
        """

        self._load_model()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an enterprise AI workflow planner. "
                    "Follow the user's instructions exactly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():

            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        input_length = inputs["input_ids"].shape[1]

        generated_ids = output_ids[0][input_length:]

        response = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        ).strip()

        return response


local_llm = LocalLLM()