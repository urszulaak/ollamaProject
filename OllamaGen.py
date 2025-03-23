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
            i = 1
            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    collected_response += chunk["message"]["content"]
                    c  = collected_response.split()
                    num_of_el = len(c)
                    if i != num_of_el:
                        i+=1
                        callback(collected_response, c[num_of_el-2], False)
                    callback(collected_response, False, False)
                
            callback(collected_response, False, True)
        threading.Thread(target=RespondFunc, daemon=True).start()