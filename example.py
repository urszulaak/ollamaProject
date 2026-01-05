def onRecognitionResult(self, recognized_text, status, end):
        def update_ui(dt):
            if end:
                if status == typeEnum.START:
                    for col_id in ['col1', 'col2', 'col3']:
                        self.ids[f'{col_id}_img'].text = str("")
                        self.ids[f'{col_id}_day'].text = str("")
                        self.ids[f'{col_id}_desc'].text = str("")
                        self.ids[f'{col_id}_H'].text = str("")
                    self.ids.content.size_hint_y = 0.5
                    self.ids.image_box.size_hint_y = 0.35
                    self.ids.columns.size_hint_y = 0.2
                    self.ids.model_response.size_hint_y = 0.6
                    self.ids.face_img.size_hint_y=1
                    self.ai_view = True
                    self.ids.model_response.text = ""
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.START.value)
                    self.ids.command.text = self.recording
                    self.voice_recorder.voiceRecord(self.onRecognitionResult, True)
                elif status == typeEnum.STOP and self.ai_view:
                    Clock.schedule_once(lambda dt: self.change_img("mask_think.png"),0)
                    user_message = recognized_text.rsplit(' ', 1)[0]
                    self.ids.command.text = user_message
                    self.chat_history.append({"role": "user", "content": user_message})
                    self.model_generate.GenerateRespond(self.ids.command.text, self.model_ai, self.rss_panel.data, self.onModelGenerate, chat_history=self.chat_history)
                elif status == typeEnum.END:
                    if self.ai_view:
                        self.ids.face_img.size_hint_y = 0.001
                        self.ai_view = False
                    else:
                        self.news_view = False
                        self.expanded_news = False
                    self.ids.content.size_hint_y = 0.5
                    self.ids.image_box.size_hint_y = 0.35
                    self.ids.model_response.size_hint_y = 0.2
                    self.ids.columns.size_hint_y = 0.6
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                    self.ids.command.text = ""
                    self.ids.model_response.text = ""
                    self.chat_history.clear()
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
                elif status == typeEnum.WEATHER and not self.ai_view:
                    self.weather = self.weather_updater._last_data
                    if self.weather is None:
                        self.ids.model_response.text =  self.config["no_connection"]
                        self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                    else:
                        self.ids.model_response.size_hint_y = 0.2
                        self.ids.columns.size_hint_y = 0.6
                        self.ids.face_img.size_hint_y=0
                        columns = [
                            ('col1', 3, 4, 5, 6),
                            ('col2', 7, 8, 9, 10),
                            ('col3', 11, 12, 13, 14)
                        ]
                        for col_id, day_idx, img_idx, desc_idx, high_idx in columns:
                            self.ids[f'{col_id}_img'].text = str(self.weather[img_idx])
                            self.ids[f'{col_id}_day'].text = str(self.weather[day_idx])
                            self.ids[f'{col_id}_desc'].text = str(self.weather[desc_idx])
                            self.ids[f'{col_id}_H'].text = str(self.weather[high_idx])
                        if self.news_view:
                            self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                        else:
                            self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                    self.do_layout()
                    if hasattr(self.ids, 'columns'):
                        self.ids.columns.do_layout()
                    if hasattr(self.ids, 'content'):
                        self.ids.content.do_layout()

                    self.canvas.ask_update()

                    Window.canvas.ask_update()
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
                elif status == typeEnum.NEWS and not self.ai_view:
                    if not self.rss_panel.data:
                        self.ids.model_response.text =  self.config["no_connection"]
                        self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config)
                    else:
                        self.news_view = True
                        self.ids.model_response.size_hint_y = 0.2
                        self.ids.columns.size_hint_y = 0.6
                        self.ids.face_img.size_hint_y=0
                        self.rss_dict = self.rss_panel.data
                        self.news = list(self.rss_dict.keys())
                        self.actuall_news = self.news[self.news_index]
                        self.ids.model_response.text = self.actuall_news
                        self.force_window_refresh()
                        self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
                elif status == typeEnum.EXPAND_NEWS and self.news_view:
                    self.expanded_news = True
                    self.ids.content.size_hint_y = 0.75
                    self.ids.image_box.size_hint_y = 0.1
                    self.ids.model_response.size_hint_y = 0.45
                    self.ids.columns.size_hint_y = 0.35
                    self.ids.face_img.size_hint_y=0
                    self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                    self.force_window_refresh()
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
                elif status == typeEnum.NEXT_NEWS and self.news_view:
                    if self.news_index < len(self.news) - 1:
                        self.news_index +=1
                        self.actuall_news = self.news[self.news_index]
                    self.ids.face_img.size_hint_y=0
                    def update_news(dt):
                        if self.expanded_news:
                            self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                        else:
                            self.ids.model_response.text = self.actuall_news
                    Clock.schedule_once(update_news)
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
                elif status == typeEnum.PREVIOUS_NEWS and self.news_view:
                    if self.news_index > 0:
                        self.news_index -=1
                        self.actuall_news = self.news[self.news_index]
                    self.ids.face_img.size_hint_y=0
                    def update_news(dt):
                        if self.expanded_news:
                            self.ids.model_response.text = f"{self.actuall_news}\n\n{self.rss_dict[self.actuall_news]}"
                        else:
                            self.ids.model_response.text = self.actuall_news
                    Clock.schedule_once(update_news)
                    self.ids.header.text = self.voice_recorder.voiceInitial(self.model_path, self.config, typeEnum.NEWS.value)
                    self.voice_recorder.voiceRecord(self.onRecognitionResult)
            else:
                self.ids.command.text = recognized_text
        Clock.schedule_once(update_ui, 0)

    def force_window_refresh():
        current_width, current_height = Window.size
        
        Window.size = (current_width + 1, current_height + 1)
        
        def restore_size(dt):
            Window.size = (current_width, current_height)
            
        Clock.schedule_once(restore_size, 0)