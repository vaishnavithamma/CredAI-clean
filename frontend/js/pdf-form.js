const DEFAULT_LOAN_FIELDS = [
    { field_key: 'full_name', label: 'Full Name', question_en: 'What is your full name?', question_hi: 'आपका पूरा नाम क्या है?', question_kn: 'ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?', type: 'text', required: true, order: 1 },
    { field_key: 'dob', label: 'Date of Birth', question_en: 'What is your date of birth? Say the day, month, and year.', question_hi: 'आपकी जन्म तिथि क्या है? दिन, महीना और साल बताएं।', question_kn: 'ನಿಮ್ಮ ಹುಟ್ಟಿದ ದಿನಾಂಕ ಏನು? ದಿನ, ತಿಂಗಳು ಮತ್ತು ವರ್ಷ ಹೇಳಿ।', type: 'date', required: true, order: 2 },
    { field_key: 'gender', label: 'Gender', question_en: 'What is your gender? Male, Female, or Other?', question_hi: 'आपका लिंग क्या है? पुरुष, महिला, या अन्य?', question_kn: 'ನಿಮ್ಮ ಲಿಂಗ ಏನು? ಪುರುಷ, ಮಹಿಳೆ, ಅಥವಾ ಇತರ?', type: 'select', required: true, order: 3 },
    { field_key: 'marital_status', label: 'Marital Status', question_en: 'Are you married or unmarried?', question_hi: 'आप विवाहित हैं या अविवाहित?', question_kn: 'ನೀವು ವಿವಾಹಿತರೇ ಅಥವಾ ಅವಿವಾಹಿತರೇ?', type: 'select', required: true, order: 4 },
    { field_key: 'dependents', label: 'Dependents', question_en: 'How many family members financially depend on you?', question_hi: 'आप पर आर्थिक रूप से कितने परिवार के सदस्य निर्भर हैं?', question_kn: 'ಆರ್ಥಿಕವಾಗಿ ನಿಮ್ಮ ಮೇಲೆ ಅವಲಂಬಿತರಾದ ಕುಟುಂಬ ಸದಸ್ಯರ ಸಂಖ್ಯೆ ಎಷ್ಟು?', type: 'number', required: true, order: 5 },
    { field_key: 'phone', label: 'Phone', question_en: 'What is your mobile phone number?', question_hi: 'आपका मोबाइल नंबर क्या है?', question_kn: 'ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಏನು?', type: 'text', required: true, order: 6 },
    { field_key: 'email', label: 'Email', question_en: 'What is your email address? Say skip if you do not have one.', question_hi: 'आपका ईमेल पता क्या है? अगर नहीं है तो स्किप कहें।', question_kn: 'ನಿಮ್ಮ ಇಮೇಲ್ ವಿಳಾಸ ಏನು? ಇಲ್ಲದಿದ್ದರೆ, ಸ್ಕಿಪ್ ಹೇಳಿ।', type: 'email', required: false, order: 7 },
    { field_key: 'address', label: 'Address', question_en: 'What is your full home address?', question_hi: 'आपका पूरा घर का पता क्या है?', question_kn: 'ನಿಮ್ಮ ಪೂರ್ಣ ಮನೆ ವಿಳಾಸ ಏನು?', type: 'text', required: true, order: 8 },
    { field_key: 'city', label: 'City', question_en: 'Which city do you live in?', question_hi: 'आप अभी किस शहर में रहते हैं?', question_kn: 'ನೀವು ಈಗ ಯಾವ ನಗರದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?', type: 'text', required: true, order: 9 },
    { field_key: 'state', label: 'State', question_en: 'Which state do you live in?', question_hi: 'आप किस राज्य में रहते हैं?', question_kn: 'ನೀವು ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?', type: 'text', required: true, order: 10 },
    { field_key: 'employment_type', label: 'Employment', question_en: 'Are you salaried, self-employed, running a business, or a farmer?', question_hi: 'आपकी नौकरी का प्रकार क्या है? क्या आप नौकरीपेशा हैं, स्व-नियोजित हैं, व्यापार चलाते हैं, या किसान हैं?', question_kn: 'ನಿಮ್ಮ ಉದ್ಯೋಗದ ರೀತಿ ಏನು? ನೀವು ನೌಕರರೇ, ಸ್ವಯಂ ಉದ್ಯೋಗಸ್ಥರೇ, ವ್ಯಾಪಾರಿಯೇ, ಅಥವಾ ರೈತರೇ?', type: 'select', required: true, order: 11 },
    { field_key: 'employer_name', label: 'Employer', question_en: 'What is the name of your employer or business?', question_hi: 'आपके नियोक्ता या व्यवसाय का नाम क्या है?', question_kn: 'ನಿಮ್ಮ ಉದ್ಯೋಗದಾತ ಅಥವಾ ವ್ಯಾಪಾರದ ಹೆಸರು ಏನು?', type: 'text', required: true, order: 12 },
    { field_key: 'monthly_income', label: 'Income', question_en: 'What is your monthly income in rupees?', question_hi: 'आपकी मासिक आय कितनी है रुपयों में?', question_kn: 'ನಿಮ್ಮ ಮಾಸಿಕ ಆದಾಯ ರೂಪಾಯಿಗಳಲ್ಲಿ ಎಷ್ಟು?', type: 'number', required: true, order: 13 },
    { field_key: 'work_experience_years', label: 'Experience', question_en: 'How many years of work experience do you have?', question_hi: 'आपके पास कितने साल का कार्य अनुभव है?', question_kn: 'ನಿಮಗೆ ಎಷ್ಟು ವರ್ಷಗಳ ಕೆಲಸದ ಅನುಭವ ಇದೆ?', type: 'number', required: true, order: 14 },
    { field_key: 'loan_amount', label: 'Loan Amount', question_en: 'How much loan amount do you need in rupees?', question_hi: 'आपको कितने रुपये का ऋण चाहिए?', question_kn: 'ನಿಮಗೆ ಎಷ್ಟು ರೂಪಾಯಿ ಸಾಲ ಬೇಕು?', type: 'number', required: true, order: 15 },
    { field_key: 'loan_purpose', label: 'Purpose', question_en: 'What will you use this loan for?', question_hi: 'आप इस ऋण का उपयोग किस लिए करेंगे?', question_kn: 'ಈ ಸಾಲವನ್ನು ಯಾವ ಉದ್ದೇಶಕ್ಕಾಗಿ ಬಳಸುತ್ತೀರಿ?', type: 'text', required: true, order: 16 },
    { field_key: 'loan_tenure_months', label: 'Tenure', question_en: 'For how many months do you want to repay the loan? For example, 12, 24, or 36.', question_hi: 'आप कितने महीनों में ऋण वापस करना चाहते हैं? जैसे 12, 24 या 36 महीने।', question_kn: 'ಸಾಲವನ್ನು ಎಷ್ಟು ತಿಂಗಳಲ್ಲಿ ತಿರುಗಿ ಕೊಡಲು ಬಯಸುತ್ತೀರಿ? ಉದಾ: 12, 24 ಅಥವಾ 36 ತಿಂಗಳು.', type: 'number', required: true, order: 17 },
    { field_key: 'pan_number', label: 'PAN Card', question_en: 'What is your PAN card number?', question_hi: 'आपका पैन कार्ड नंबर क्या है?', question_kn: 'ನಿಮ್ಮ ಪ್ಯಾನ್ ಕಾರ್ಡ್ ಸಂಖ್ಯೆ ಏನು?', type: 'text', required: true, order: 18 },
    { field_key: 'aadhaar_number', label: 'Aadhaar Card', question_en: 'What is your Aadhaar card number?', question_hi: 'आपका आधार कार्ड नंबर क्या है?', question_kn: 'ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್ ಸಂಖ್ಯೆ ಏನು?', type: 'text', required: true, order: 19 },
    { field_key: 'own_property', label: 'Own Property', question_en: 'Do you own a house or any property? Say yes or no.', question_hi: 'क्या आपके पास घर या कोई संपत्ति है? हाँ या नहीं कहें।', question_kn: 'ನಿಮ್ಮ ಬಳಿ ಮನೆ ಅಥವಾ ಆಸ್ತಿ ಇದೆಯೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಹೇಳಿ।', type: 'boolean', required: true, order: 20 },
    { field_key: 'own_vehicle', label: 'Own Vehicle', question_en: 'Do you own a vehicle like a car or motorcycle? Say yes or no.', question_hi: 'क्या आपके पास कार या मोटरसाइकिल जैसा वाहन है? हाँ या नहीं कहें।', question_kn: 'ನಿಮ್ಮ ಬಳಿ ಕಾರು ಅಥವಾ ಮೋಟರ್ಸೈಕಲ್ ಇದೆಯೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಹೇಳಿ।', type: 'boolean', required: true, order: 21 }
];

async function parsePDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/pdf/parse', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.success && data.fields.length > 5) {
            return data.fields;
        }
    } catch (err) {
        console.error("PDF Parsing Error:", err);
    }
    return DEFAULT_LOAN_FIELDS;
}
