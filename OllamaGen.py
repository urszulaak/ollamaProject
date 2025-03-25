import ollama
import threading

class OllamaGen():
    def GenerateRespond(self, recognized_text, language, callback):
        file_path=""
        model_ai=""
        if language == 1:
            pass
        else:
            file_path = './system_note_pl.txt'
            model_ai = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
        with open(file_path, 'r') as file:
            system_note = file.read()
        ollama.create(model="ai_model", from_=model_ai, system=system_note)
        def RespondFunc():
            response = ollama.chat(
                model="ai_model",
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
                    else:
                        callback(collected_response, False, False)
                
            callback(collected_response, c[num_of_el-1], False)
            callback(collected_response, False, True)
        threading.Thread(target=RespondFunc, daemon=True).start()