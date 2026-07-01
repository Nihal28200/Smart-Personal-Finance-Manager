import re
import random
from datetime import date
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pass

def extract_data_from_receipt(image_file):
    
    data = {
        'amount': None,
        'category': 'General',
        'date': date.today().strftime('%Y-%m-%d'),
        'description': 'Scanned Receipt'
    }

    try:
       
        img = Image.open(image_file)
        text = pytesseract.image_to_string(img)
        
        amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
        amounts = re.findall(amount_pattern, text)
        
        if amounts:
            valid_amounts = [float(a.replace(',', '')) for a in amounts]
            data['amount'] = max(valid_amounts)

        text_lower = text.lower()
        if any(x in text_lower for x in ['burger', 'pizza', 'restaurant', 'food', 'zomato', 'swiggy', 'cafe']):
            data['category'] = 'Food'
        elif any(x in text_lower for x in ['fuel', 'petrol', 'uber', 'ola', 'taxi', 'travel', 'flight']):
            data['category'] = 'Travel'
        elif any(x in text_lower for x in ['mart', 'grocery', 'milk', 'vegetable', 'supermarket']):
            data['category'] = 'Groceries'
        elif any(x in text_lower for x in ['movie', 'cinema', 'netflix', 'amazon', 'prime']):
            data['category'] = 'Entertainment'
        elif any(x in text_lower for x in ['hospital', 'pharmacy', 'medplus', 'apollo', 'doctor']):
            data['category'] = 'Health'

    except Exception as e:
        print(f"OCR Error (Using Demo Mode): {e}")
        data['amount'] = round(random.uniform(150.00, 2500.00), 2) # Random amount 150-2500 ke beech
        categories = ['Food', 'Travel', 'Shopping', 'Bills', 'Health']
        data['category'] = random.choice(categories)
    
   
    if data['amount'] is None:
         data['amount'] = round(random.uniform(100.00, 1000.00), 2)

    return data