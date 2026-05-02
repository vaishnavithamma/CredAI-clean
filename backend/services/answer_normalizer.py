import re
from dateutil import parser as date_parser

class AnswerNormalizer:
    # HINDI number words
    HINDI_NUMBERS = {
        "शून्य": 0, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9,
        "दस": 10, "ग्यारह": 11, "बारह": 12, "बीस": 20, "तीस": 30, "चालीस": 40, "पचास": 50,
        "साठ": 60, "सत्तर": 70, "अस्सी": 80, "नब्बे": 90, "सौ": 100,
        "हज़ार": 1000, "हजार": 1000, "लाख": 100000, "करोड़": 10000000, "करोड": 10000000
    }
    
    # KANNADA number words
    KANNADA_NUMBERS = {
        "ಸೊನ್ನೆ": 0, "ಒಂದು": 1, "ಎರಡು": 2, "ಮೂರು": 3, "ನಾಲ್ಕು": 4, "ಐದು": 5, "ಆರು": 6, "ಏಳು": 7, "ಎಂಟು": 8, "ಒಂಬತ್ತು": 9,
        "ಹತ್ತು": 10, "ಇಪ್ಪತ್ತು": 20, "ಮೂವತ್ತು": 30, "ನಲವತ್ತು": 40,
        "ಐವತ್ತು": 50, "ಅರವತ್ತು": 60, "ಎಪ್ಪತ್ತು": 70, "ಎಂಭತ್ತು": 80, "ಎಂಬತ್ತು": 80,
        "ತೊಂಭತ್ತು": 90, "ತೊಂಬತ್ತು": 90, "ನೂರು": 100, "ಸಾವಿರ": 1000, "ಲಕ್ಷ": 100000, "ಕೋಟಿ": 10000000
    }
    
    YES_WORDS = ["yes", "yeah", "yep", "हाँ", "हां", "ji", "ಹೌದು", "ha"]
    NO_WORDS = ["no", "nope", "nahi", "नहीं", "नहि", "ಇಲ್ಲ"]

    def normalize(self, field_key, raw_answer, language, field_type):
        raw_answer = raw_answer.lower().strip()
        confidence = 0.9

        # Handle simple skip logic internally if passed
        if raw_answer in ["skip", "स्किप", "ಸ್ಕಿಪ್", "ಮುಂದೆ", "छोड़ो"]:
            return {
                "success": True, "field_key": field_key, "raw_answer": raw_answer,
                "normalized_value": None, "display_value": "Skipped",
                "confidence": 1.0, "needs_confirmation": False
            }

        try:
            if field_type == "number":
                val, disp = self._parse_number(raw_answer, language)
                if val is None:
                    return {"needs_confirmation": True, "suggested_value": raw_answer, "confirmation_question": "I didn't hear a valid number. Could you repeat?"}
                return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": val, "display_value": disp, "confidence": confidence, "needs_confirmation": False}

            elif field_type == "date":
                val, disp = self._parse_date(raw_answer)
                if val is None:
                    return {"needs_confirmation": True, "suggested_value": raw_answer, "confirmation_question": f"Did you mean {raw_answer}?"}
                return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": val, "display_value": disp, "confidence": confidence, "needs_confirmation": False}

            elif field_type == "boolean":
                if any(w in raw_answer for w in self.YES_WORDS):
                    return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Y", "display_value": "Yes", "confidence": confidence, "needs_confirmation": False}
                if any(w in raw_answer for w in self.NO_WORDS):
                    return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "N", "display_value": "No", "confidence": confidence, "needs_confirmation": False}
                return {"needs_confirmation": True, "suggested_value": raw_answer, "confirmation_question": "Please say Yes or No."}

            elif field_type == "select":
                if field_key == "gender":
                    if any(w in raw_answer for w in ["male", "man", "पुरुष", "ಪುರುಷ"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Male", "display_value": "Male", "confidence": confidence, "needs_confirmation": False}
                    if any(w in raw_answer for w in ["female", "woman", "महिला", "ಮಹಿಳೆ"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Female", "display_value": "Female", "confidence": confidence, "needs_confirmation": False}
                
                if field_key == "employment_type":
                    if any(w in raw_answer for w in ["salary", "salaried", "job", "नौकरी", "ಉದ್ಯೋಗ"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Working", "display_value": "Salaried", "confidence": confidence, "needs_confirmation": False}
                    if any(w in raw_answer for w in ["business", "व्यापार", "ವ್ಯಾಪಾರ", "self", "commercial"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Commercial associate", "display_value": "Business", "confidence": confidence, "needs_confirmation": False}
                    if any(w in raw_answer for w in ["pension", "रिटायर"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Pensioner", "display_value": "Pensioner", "confidence": confidence, "needs_confirmation": False}
                
                if field_key == "marital_status":
                    if any(w in raw_answer for w in ["single", "unmarried", "अविवाहित", "ಅವಿವಾಹಿತ"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Single / not married", "display_value": "Single", "confidence": confidence, "needs_confirmation": False}
                    if any(w in raw_answer for w in ["married", "विवाहित", "ವಿವಾಹಿತ"]):
                        return {"success": True, "field_key": field_key, "raw_answer": raw_answer, "normalized_value": "Married", "display_value": "Married", "confidence": confidence, "needs_confirmation": False}

            # Default text extraction (PAN, Aadhaar, Names)
            cleaned_text = raw_answer.title() if field_type != "email" else raw_answer.lower()
            if field_key == "pan_number":
                cleaned_text = re.sub(r'[\s\-]', '', raw_answer).upper()
            elif field_key == "aadhaar_number":
                cleaned_text = re.sub(r'\D', '', raw_answer)
            
            return {
                "success": True, "field_key": field_key, "raw_answer": raw_answer,
                "normalized_value": cleaned_text, "display_value": cleaned_text,
                "confidence": confidence, "needs_confirmation": False
            }

        except Exception as e:
            return {"needs_confirmation": True, "suggested_value": raw_answer, "confirmation_question": "I didn't understand. Could you repeat?"}

    def _parse_number(self, text, language):
        # 1. Try simple digit extraction
        digits = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
        if digits:
            val = float(digits[0].replace(',', ''))
            # Scale if words like lakh/thousand are present
            if any(w in text for w in ["lakh", "लाख", "ಲಕ್ಷ"]): val *= 100000
            if any(w in text for w in ["thousand", "हज़ार", "हजार", "ಸಾವಿರ"]): val *= 1000
            return val, f"{int(val):,}"

        # 2. Try English word2number
        if language == "en":
            try:
                from word2number import w2n
                val = w2n.word_to_num(text)
                return float(val), f"{int(val):,}"
            except:
                pass
        
        # 3. Custom Regional Parser (Hindi / Kannada)
        words = text.split()
        total = 0
        current = 0
        dict_to_use = self.HINDI_NUMBERS if language == "hi" else self.KANNADA_NUMBERS
        
        for word in words:
            if word in dict_to_use:
                num = dict_to_use[word]
                if num == 100:
                    current = current * 100 if current != 0 else 100
                elif num >= 1000:
                    total += (current if current != 0 else 1) * num
                    current = 0
                else:
                    current += num

        total += current
        if total > 0:
            return float(total), f"{int(total):,}"

        return None, None

    def _parse_date(self, text):
        try:
            # Handle standard natural language dates
            parsed = date_parser.parse(text, fuzzy=True)
            return parsed.strftime("%Y-%m-%d"), parsed.strftime("%d %b %Y")
        except:
            return None, None
