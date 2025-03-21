import ollama
import threading

class OllamaGen():
    def GenerateRespond(self, recognized_text, model_ai, callback):
        def RespondFunc():
            response = ollama.chat(
                model=model_ai,
                messages=[
                    {"role": "user", "content": recognized_text},
                ],
                stream = True,
            )
            collected_response = ""
            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    collected_response += chunk["message"]["content"]
                    callback(collected_response, False)
                
            callback(collected_response, True)
        threading.Thread(target=RespondFunc, daemon=True).start()