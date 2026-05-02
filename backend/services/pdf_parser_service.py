import pdfplumber
import pypdf
import io
import re

class PDFParserService:
    FIELD_SYNONYM_MAP = {
        "full name": "full_name",
        "applicant name": "full_name",
        "name of applicant": "full_name",
        "name": "full_name",
        "date of birth": "dob",
        "dob": "dob",
        "birth date": "dob",
        "mobile": "phone",
        "mobile number": "phone",
        "phone": "phone",
        "phone number": "phone",
        "email": "email",
        "email address": "email",
        "monthly income": "monthly_income",
        "net monthly income": "monthly_income",
        "salary": "monthly_income",
        "income": "monthly_income",
        "loan amount": "loan_amount",
        "required loan": "loan_amount",
        "loan required": "loan_amount",
        "purpose": "loan_purpose",
        "loan purpose": "loan_purpose",
        "pan": "pan_number",
        "pan number": "pan_number",
        "aadhaar": "aadhaar_number",
        "aadhaar number": "aadhaar_number",
        "gender": "gender",
        "city": "city",
        "address": "address",
        "employment type": "employment_type",
        "occupation": "employment_type",
        "employer": "employer_name",
        "company name": "employer_name",
    }

    MULTILINGUAL_QUESTIONS = {
        "full_name": {
            "en": "What is your full name?",
            "hi": "आपका पूरा नाम क्या है?",
            "kn": "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?",
            "type": "text", "label": "Full Name", "order": 1
        },
        "dob": {
            "en": "What is your date of birth? Please say the day, month, and year.",
            "hi": "आपकी जन्म तिथि क्या है? दिन, महीना और साल बताएं।",
            "kn": "ನಿಮ್ಮ ಹುಟ್ಟಿದ ದಿನಾಂಕ ಏನು? ದಿನ, ತಿಂಗಳು ಮತ್ತು ವರ್ಷ ಹೇಳಿ।",
            "type": "date", "label": "Date of Birth", "order": 2
        },
        "gender": {
            "en": "What is your gender? Male, Female, or Other?",
            "hi": "आपका लिंग क्या है? पुरुष, महिला, या अन्य?",
            "kn": "ನಿಮ್ಮ ಲಿಂಗ ಏನು? ಪುರುಷ, ಮಹಿಳೆ, ಅಥವಾ ಇತರ?",
            "type": "select", "label": "Gender", "order": 3
        },
        "marital_status": {
            "en": "What is your marital status? Are you married or unmarried?",
            "hi": "आपकी वैवाहिक स्थिति क्या है? आप विवाहित हैं या अविवाहित?",
            "kn": "ನಿಮ್ಮ ವಿವಾಹ ಸ್ಥಿತಿ ಏನು? ನೀವು ವಿವಾಹಿತರೇ ಅಥವಾ ಅವಿವಾಹಿತರೇ?",
            "type": "select", "label": "Marital Status", "order": 4
        },
        "dependents": {
            "en": "How many family members financially depend on you?",
            "hi": "आप पर आर्थिक रूप से कितने परिवार के सदस्य निर्भर हैं?",
            "kn": "ಆರ್ಥಿಕವಾಗಿ ನಿಮ್ಮ ಮೇಲೆ ಅವಲಂಬಿತರಾದ ಕುಟುಂಬ ಸದಸ್ಯರ ಸಂಖ್ಯೆ ಎಷ್ಟು?",
            "type": "number", "label": "Dependents", "order": 5
        },
        "phone": {
            "en": "What is your mobile phone number?",
            "hi": "आपका मोबाइल नंबर क्या है?",
            "kn": "ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?",
            "type": "text", "label": "Phone Number", "order": 6
        },
        "email": {
            "en": "What is your email address? If you don't have one, say skip.",
            "hi": "आपका ईमेल पता क्या है? अगर नहीं है तो स्किप कहें।",
            "kn": "ನಿಮ್ಮ ಇಮೇಲ್ ವಿಳಾಸ ಏನು? ಇಲ್ಲದಿದ್ದರೆ, ಸ್ಕಿಪ್ ಹೇಳಿ।",
            "type": "email", "label": "Email Address", "order": 7
        },
        "address": {
            "en": "What is your full home address?",
            "hi": "आपका पूरा घर का पता क्या है?",
            "kn": "ನಿಮ್ಮ ಪೂರ್ಣ ಮನೆ ವಿಳಾಸ ಏನು?",
            "type": "text", "label": "Home Address", "order": 8
        },
        "city": {
            "en": "Which city do you currently live in?",
            "hi": "आप अभी किस शहर में रहते हैं?",
            "kn": "ನೀವು ಈಗ ಯಾವ ನಗರದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?",
            "type": "text", "label": "City", "order": 9
        },
        "state": {
            "en": "Which state do you live in?",
            "hi": "आप किस राज्य में रहते हैं?",
            "kn": "ನೀವು ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?",
            "type": "text", "label": "State", "order": 10
        },
        "employment_type": {
            "en": "What type of employment do you have? Are you salaried, self-employed, running a business, or a farmer?",
            "hi": "आपकी नौकरी का प्रकार क्या है? क्या आप नौकरीपेशा हैं, स्व-नियोजित हैं, व्यापार चलाते हैं, या किसान हैं?",
            "kn": "ನಿಮ್ಮ ಉದ್ಯೋಗದ ರೀತಿ ಏನು? ನೀವು ನೌಕರರೇ, ಸ್ವಯಂ ಉದ್ಯೋಗಸ್ಥರೇ, ವ್ಯಾಪಾರಿಯೇ, ಅಥವಾ ರೈತರೇ?",
            "type": "select", "label": "Employment Type", "order": 11
        },
        "employer_name": {
            "en": "What is the name of your employer or business?",
            "hi": "आपके नियोक्ता या व्यवसाय का नाम क्या है?",
            "kn": "ನಿಮ್ಮ ಉದ್ಯೋಗದಾತ ಅಥವಾ ವ್ಯಾಪಾರದ ಹೆಸರು ಏನು?",
            "type": "text", "label": "Employer/Business Name", "order": 12
        },
        "monthly_income": {
            "en": "What is your monthly income in rupees?",
            "hi": "आपकी मासिक आय कितनी है रुपयों में?",
            "kn": "ನಿಮ್ಮ ಮಾಸಿಕ ಆದಾಯ ರೂಪಾಯಿಗಳಲ್ಲಿ ಎಷ್ಟು?",
            "type": "number", "label": "Monthly Income", "order": 13
        },
        "work_experience_years": {
            "en": "How many years of work experience do you have?",
            "hi": "आपके पास कितने साल का कार्य अनुभव है?",
            "kn": "ನಿಮಗೆ ಎಷ್ಟು ವರ್ಷಗಳ ಕೆಲಸದ ಅನುಭವ ಇದೆ?",
            "type": "number", "label": "Work Experience (Years)", "order": 14
        },
        "loan_amount": {
            "en": "How much loan amount do you need in rupees?",
            "hi": "आपको कितने रुपये का ऋण चाहिए?",
            "kn": "ನಿಮಗೆ ಎಷ್ಟು ರೂಪಾಯಿ ಸಾಲ ಬೇಕು?",
            "type": "number", "label": "Loan Amount", "order": 15
        },
        "loan_purpose": {
            "en": "What will you use this loan for?",
            "hi": "आप इस ऋण का उपयोग किस लिए करेंगे?",
            "kn": "ಈ ಸಾಲವನ್ನು ಯಾವ ಉದ್ದೇಶಕ್ಕಾಗಿ ಬಳಸುತ್ತೀರಿ?",
            "type": "text", "label": "Loan Purpose", "order": 16
        },
        "loan_tenure_months": {
            "en": "For how many months do you want to repay the loan? For example, 12, 24, or 36 months.",
            "hi": "आप कितने महीनों में ऋण वापस करना चाहते हैं? जैसे 12, 24 या 36 महीने।",
            "kn": "ಸಾಲವನ್ನು ಎಷ್ಟು ತಿಂಗಳಲ್ಲಿ ತಿರುಗಿ ಕೊಡಲು ಬಯಸುತ್ತೀರಿ? ಉದಾ: 12, 24 ಅಥವಾ 36 ತಿಂಗಳು.",
            "type": "number", "label": "Loan Tenure (Months)", "order": 17
        },
        "pan_number": {
            "en": "What is your PAN card number? It has 10 characters — 5 letters, 4 digits, and 1 letter.",
            "hi": "आपका पैन कार्ड नंबर क्या है? इसमें 10 अक्षर होते हैं।",
            "kn": "ನಿಮ್ಮ ಪ್ಯಾನ್ ಕಾರ್ಡ್ ಸಂಖ್ಯೆ ಏನು? ಇದರಲ್ಲಿ 10 ಅಕ್ಷರಗಳಿವೆ।",
            "type": "text", "label": "PAN Number", "order": 18
        },
        "aadhaar_number": {
            "en": "What is your Aadhaar card number? It is a 12-digit number.",
            "hi": "आपका आधार कार्ड नंबर क्या है? यह 12 अंकों का नंबर है।",
            "kn": "ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್ ಸಂಖ್ಯೆ ಏನು? ಇದು 12 ಅಂಕಿಗಳ ಸಂಖ್ಯೆ।",
            "type": "text", "label": "Aadhaar Number", "order": 19
        },
        "own_property": {
            "en": "Do you own a house or any property? Say yes or no.",
            "hi": "क्या आपके पास घर या कोई संपत्ति है? हाँ या नहीं कहें।",
            "kn": "ನಿಮ್ಮ ಬಳಿ ಮನೆ ಅಥವಾ ಆಸ್ತಿ ಇದೆಯೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಹೇಳಿ।",
            "type": "boolean", "label": "Own Property?", "order": 20
        },
        "own_vehicle": {
            "en": "Do you own a vehicle like a car or motorcycle? Say yes or no.",
            "hi": "क्या आपके पास कार या मोटरसाइकिल जैसा वाहन है? हाँ या नहीं कहें।",
            "kn": "ನಿಮ್ಮ ಬಳಿ ಕಾರು ಅಥವಾ ಮೋಟರ್ಸೈಕಲ್ ಇದೆಯೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಹೇಳಿ।",
            "type": "boolean", "label": "Own Vehicle?", "order": 21
        }
    }

    def parse_pdf(self, file_bytes: bytes) -> dict:
        extracted_keys = set()
        
        # 1. Attempt AcroForm parsing first (PyPDF)
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            fields = reader.get_fields()
            if fields:
                for f_name in fields.keys():
                    cleaned = f_name.lower().replace("_", " ").strip()
                    for synonym, canonical in self.FIELD_SYNONYM_MAP.items():
                        if synonym in cleaned:
                            extracted_keys.add(canonical)
                            break
        except Exception as e:
            print(f"PyPDF AcroForm parsing error: {e}")

        # 2. Fallback / Supplement: pdfplumber text layout parsing
        if len(extracted_keys) < 5:
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            lines = text.split("\n")
                            for line in lines:
                                cleaned = line.lower().strip()
                                for synonym, canonical in self.FIELD_SYNONYM_MAP.items():
                                    # Simple regex to check if synonym acts as a label (ends with :, ____, or just raw)
                                    pattern = r"\b" + re.escape(synonym) + r"\b"
                                    if re.search(pattern, cleaned):
                                        extracted_keys.add(canonical)
            except Exception as e:
                print(f"pdfplumber text parsing error: {e}")

        # If we failed to extract much, use ALL default fields
        if len(extracted_keys) < 5:
            extracted_keys = set(self.MULTILINGUAL_QUESTIONS.keys())

        # Construct final schema
        final_fields = []
        for key in self.MULTILINGUAL_QUESTIONS.keys():
            if key in extracted_keys:
                q_data = self.MULTILINGUAL_QUESTIONS[key]
                final_fields.append({
                    "field_key": key,
                    "label": q_data["label"],
                    "question_en": q_data["en"],
                    "question_hi": q_data["hi"],
                    "question_kn": q_data["kn"],
                    "type": q_data["type"],
                    "required": True,
                    "order": q_data["order"]
                })
        
        final_fields.sort(key=lambda x: x["order"])

        return {
            "success": True,
            "form_title": "Parsed Loan Application",
            "total_fields": len(final_fields),
            "fields": final_fields
        }
