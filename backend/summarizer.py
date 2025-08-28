from transformers import BartForConditionalGeneration, BartTokenizer

class Summarizer:
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        self.max_input_tokens = 1024  # BART limit

    def chunk_text(self, text):
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            token_len = len(self.tokenizer.encode(current_chunk + sentence, truncation=False))
            if token_len <= self.max_input_tokens:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def summarize_text(self, text, max_length=150, min_length=50):
        chunks = self.chunk_text(text)
        summaries = []
        for chunk in chunks:
            inputs = self.tokenizer([chunk], max_length=self.max_input_tokens, return_tensors='pt', truncation=True)
            summary_ids = self.model.generate(
                inputs['input_ids'], 
                num_beams=4, 
                max_length=max_length, 
                min_length=min_length, 
                early_stopping=True
            )
            summaries.append(self.tokenizer.decode(summary_ids[0], skip_special_tokens=True))
        final_summary = " ".join(summaries)
        return final_summary
