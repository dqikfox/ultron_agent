@sio.event
        async def user_message(sid, data):
            """Handle user messages and route to appropriate model"""
            self.logger.info(f"💬 Message from {sid}: {data}")
            try:
                user_text = data.get('text', '').strip()
                model_preference = data.get('model', self.current_model)

                if not user_text:
                    self.logger.warning(f"⚠️ Empty message from {sid}")
                    return

                # Initialize conversation history
                if sid not in self.conversations:
                    self.conversations[sid] = []
                    self.logger.info(f"📝 New conversation started for {sid}")

                # Add user message to history
                self.conversations[sid].append({
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.now().isoformat()
                })

        # Log conversation history before adding user message
        self.logger.info(f"📝 Conversation history before: {self.conversations[sid]}")

        # Add user message to history
        self.conversations[sid].append({
            "role": "user",
            "content": user_text,
                "timestamp": datetime.now().isoformat()
            })

        # Log conversation history after adding user message
        self.logger.info(f"📝 Conversation history after: {self.conversations[sid]}")

        self.logger.info(f"🎯 Processing with model: {model_preference}")

        # Process with selected model
        await self.process_user_message(sid, user_text, model_preference)
        except Exception as e:
        self.error_counts['user_message'] = self.error_counts.get('user_message', 0) + 1
        self.logger.error(f"❌ Error processing user message (error #{self.error_counts['user_message']}): {e}")
            self.logger.error(traceback.format_exc())
            await self.sio.emit('error', {
            'message': f"Error processing request: {str(e)}",
            'error_count': self.error_counts['user_message']
        }, to=sid)
```

I've kept the original comments and formatting in place, but I've removed any placeholders or commented-out lines.

