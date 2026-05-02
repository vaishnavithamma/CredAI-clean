class QuestionEngine:
    def get_next_question(self, fields, answers, language):
        for field in fields:
            if field.get("required", True) and not answers.get(field["field_key"]):
                # Determine language key
                question_key = f"question_{language}"
                question_text = field.get(question_key)
                
                # Fallback to English if translation is missing
                if not question_text:
                    question_text = field.get("question_en", "Missing question text")
                    
                return {
                    "completed": False,
                    "field_key": field["field_key"],
                    "question_text": question_text,
                    "type": field.get("type", "text"),
                    "label": field.get("label", field["field_key"]),
                    "progress": self._calc_progress(fields, answers)
                }
        return {"completed": True}

    def _calc_progress(self, fields, answers):
        required = [f for f in fields if f.get("required", True)]
        answered = [f for f in required if answers.get(f["field_key"])]
        pct = round((len(answered) / max(len(required), 1)) * 100)
        return {
            "total": len(required),
            "answered": len(answered),
            "percent": pct
        }
