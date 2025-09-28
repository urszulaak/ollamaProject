import ollama
import threading

class OllamaGen():
    def GenerateRespond(self, recognized_text, language, news, callback, chat_history=None):
        file_path=""
        model_ai=""
        file_path = language["note"]
        model_ai = language["ollama_model"]
        with open(file_path, 'r') as file:
            system_note = file.read()
        system_note += str(news)
        ollama.create(model="ai_model", from_=model_ai, system=system_note)

        messages = []
        if chat_history:
            messages.extend(chat_history)
        else:
            messages.append({"role":"user","content": recognized_text})

        def RespondFunc():
            response = ollama.chat(
                model="ai_model",
                messages=messages,
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
                    else:
                        callback(collected_response, False, False)
            try:
                callback(collected_response, c[num_of_el-1], False)
            except ValueError:
                print("ValueError",c)
            callback(collected_response, False, True)
        threading.Thread(target=RespondFunc, daemon=True).start()