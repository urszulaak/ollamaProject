from BasicApp import BasicApp

if __name__ == "__main__":

    exit_loop = True
    
    while exit_loop:
        # language = int(input("Choose Language (1-English, 2-Polish): "))
        language = 2
        if language == 1:
            model_path = "vosk-model-en-us-0.22-lgraph"
            model_ai = "llama3.1:8b"
            exit_loop = False
        elif language == 2:
            model_path = "vosk-model-small-pl-0.22"
            model_ai = "SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M"
            exit_loop = False
        else:
            print("Wrong language")

    app = BasicApp(language, model_path)
    app.run()