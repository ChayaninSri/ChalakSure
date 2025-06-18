import pandas as pd

def check_disclaimers(nutrients):
    """
    Check nutrient values against thresholds and return appropriate disclaimers.
    
    Args:
        nutrients (dict): Dictionary containing nutrient values with keys:
            - 'total_fat'
            - 'saturated_fat'
            - 'cholesterol'
            - 'sodium'
            - 'total_sugars'
            
    Returns:
        list: List of disclaimer messages for nutrients that exceed thresholds
    """
    # Read disclaimer rules
    rules_df = pd.read_csv('disclaimer_rules.csv')
    
    # Map Thai nutrient names to English keys and units
    nutrient_map = {
        'total_fat': {'thai': 'ไขมันทั้งหมด', 'unit': 'กรัม'},
        'saturated_fat': {'thai': 'ไขมันอิ่มตัว', 'unit': 'กรัม'},
        'cholesterol': {'thai': 'คอเลสเตอรอล', 'unit': 'มิลลิกรัม'},
        'sodium': {'thai': 'โซเดียม', 'unit': 'มิลลิกรัม'}, 
        'total_sugars': {'thai': 'น้ำตาลทั้งหมด', 'unit': 'กรัม'}
    }
    
    disclaimers = []
    
    # Check each nutrient against threshold
    for eng_name, info in nutrient_map.items():
        if eng_name not in nutrients:
            continue
            
        value = nutrients[eng_name]
        thai_name = info['thai']
        unit = info['unit']
        
        # Find threshold for this nutrient
        rule = rules_df[rules_df['nutrient'] == thai_name]
        if not rule.empty:
            threshold = rule['threshold'].iloc[0]
            
            # If value is strictly greater than threshold, add disclaimer
            if value > threshold:
                disclaimer = {
                    'nutrient': thai_name,
                    'value': value,
                    'threshold': threshold,
                    'unit': unit,
                    'message': f"⚠️ {thai_name} {value:.1f} {unit} (เกินค่าที่กำหนด {threshold:.1f} {unit})\n"
                             f"ต้องมีคำชี้แจง (Disclaimer) ประกอบคำกล่าวอ้าง: มี{thai_name}ต่อหน่วยบริโภค {value:.1f} {unit}"
                }
                disclaimers.append(disclaimer)
    
    return disclaimers

def display_disclaimers(nutrients):
    """
    Display all applicable disclaimers for given nutrient values.
    
    Args:
        nutrients (dict): Dictionary containing nutrient values
    """
    disclaimers = check_disclaimers(nutrients)
    
    if disclaimers:
        print("\nRequired Disclaimers:")
        for disclaimer in disclaimers:
            print(f"- {disclaimer['message']}")
    else:
        print("\nNo disclaimers required.") 