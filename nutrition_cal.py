import math
from typing import Dict, Optional, Union, List, Any

def round_nutrition_value(value: float, nutrient_type: str = "other", precision: int = 2) -> float:
    """
    Round nutrition value according to Thai FDA regulations.
    
    Args:
        value: The value to round
        nutrient_type: Type of nutrient (energy, fat, trans_fat, cholesterol, sodium, protein, etc.)
        precision: Default precision (used only for nutrients not specifically listed)
        
    Returns:
        Rounded value according to regulations
    """
    if value is None:
        return None
        
    # Convert to float to ensure proper comparison
    value = float(value)
    
    # Convert nutrient_type to string to ensure .lower() can be called
    nutrient_type = str(nutrient_type)
    
    # Energy (kcal)
    if nutrient_type.lower() in ["energy", "พลังงาน", "calories", "พลังงานจากไขมัน"]:
        if value < 5:
            return 0
        elif value < 50:
            # Round to nearest 5
            return round(value / 5) * 5
        else:
            # Round to nearest 10
            return round(value / 10) * 10
    
    # Total fat, Saturated fat (g)
    elif nutrient_type.lower() in ["fat", "saturated_fat", "ไขมันทั้งหมด", "ไขมันอิ่มตัว", "ไขมัน"]:
        if value < 0.5:
            return 0
        elif value < 5:
            # Round to nearest 0.5
            return round(value * 2) / 2
        else:
            # Round to nearest 1
            return round(value)
    
    # Trans fat (g)
    elif nutrient_type.lower() in ["trans_fat", "ไขมันทรานส์"]:
        if value == 0:
            return 0
        elif value < 0.5:
            # For trans fat < 0.5, we need special handling in display function
            # Return a small negative value as a flag
            return -0.1  # Flag for "less than 0.5"
        elif value < 5:
            # Round to nearest 0.5
            return round(value * 2) / 2
        else:
            # Round to nearest 1
            return round(value)
    
    # Cholesterol (mg)
    elif nutrient_type.lower() in ["cholesterol", "คอเลสเตอรอล"]:
        if value < 2:
            return 0
        elif value < 5:
            # For cholesterol < 5, we need special handling in display function
            return -0.2  # Flag for "less than 5"
        else:
            # Round to nearest 5
            return round(value / 5) * 5
    
    # Protein, Carbohydrate, Fiber, Sugar (g)
    elif nutrient_type.lower() in ["protein", "carbohydrate", "fiber", "sugar", 
                                  "โปรตีน", "คาร์โบไฮเดรต", "ใยอาหาร", "น้ำตาล"]:
        if value < 0.5:
            return 0
        elif value < 1:
            # For values < 1, we need special handling in display function
            return -0.3  # Flag for "less than 1"
        else:
            # Round to nearest 1
            return round(value)
    
    # Sodium, Potassium (mg)
    elif nutrient_type.lower() in ["sodium", "potassium", "โซเดียม", "โพแทสเซียม"]:
        if value < 5:
            return 0
        elif value <= 140:
            # Round to nearest 5
            return round(value / 5) * 5
        else:
            # Round to nearest 10
            return round(value / 10) * 10
    
    # Default rounding for other nutrients
    else:
        if value >= 100:
            # Round to whole numbers for large values
            return round(value)
        elif value >= 10:
            # Round to 1 decimal place for medium values
            return round(value * 10) / 10
        else:
            # Round to the specified precision for small values
            return round(value * 10**precision) / 10**precision

def round_rdi_percent(value: float) -> float:
    """Round %RDI for vitamins and minerals according to custom rules.
    - Between 5 and 50 -> nearest multiple of 5
    - Above 50 -> nearest multiple of 10
    Other values stay the same (rounded to 1 decimal place)
    """
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if 5 <= value <= 50:
        return round(value / 5) * 5
    elif value > 50:
        return round(value / 10) * 10
    else:
        return round(value, 1)

def format_nutrition_display(value: Optional[float], nutrient_type: str = "other", unit: str = "g") -> str:
    """
    Format nutrition value for display according to Thai FDA regulations.
    
    Args:
        value: The nutrition value
        nutrient_type: Type of nutrient (energy, fat, trans_fat, cholesterol, sodium, protein, etc.)
        unit: Unit for the value (g, mg, kcal, etc.)
        
    Returns:
        Formatted string with value and unit according to regulations
    """
    if value is None:
        return "-"
    
    # Handle special cases with negative flags
    if value == -0.1:  # Trans fat < 0.5
        return f"น้อยกว่า 0.5 {unit}"
    elif value == -0.2:  # Cholesterol < 5
        return f"น้อยกว่า 5 {unit}"
    elif value == -0.3:  # Protein/Carb/Fiber/Sugar < 1
        return f"น้อยกว่า 1 {unit}"
        
    # Convert nutrient_type to string to ensure .lower() can be called
    nutrient_type = str(nutrient_type)
    
    # Format based on nutrient type and value
    if nutrient_type.lower() in ["energy", "พลังงาน", "calories"]:
        return f"{int(value)} {unit}"
    elif nutrient_type.lower() in ["fat", "saturated_fat", "ไขมันทั้งหมด", "ไขมันอิ่มตัว", "ไขมัน"]:
        if value < 5:
            return f"{value:.1f} {unit}"
        else:
            return f"{int(value)} {unit}"
    elif nutrient_type.lower() in ["trans_fat", "ไขมันทรานส์"]:
        if value < 5:
            return f"{value:.1f} {unit}"
        else:
            return f"{int(value)} {unit}"
    elif nutrient_type.lower() in ["protein", "carbohydrate", "fiber", "sugar", 
                                  "โปรตีน", "คาร์โบไฮเดรต", "ใยอาหาร", "น้ำตาล"]:
        return f"{int(value)} {unit}"
    elif nutrient_type.lower() in ["sodium", "potassium", "โซเดียม", "โพแทสเซียม", 
                                   "cholesterol", "คอเลสเตอรอล"]:
        return f"{int(value)} {unit}"
    else:
        # Format based on magnitude for other nutrients
        if value >= 100:
            return f"{int(value)} {unit}"
        elif value >= 10:
            return f"{value:.1f} {unit}"
        else:
            return f"{value:.2f} {unit}"

def adjust_per_100_to_serving(
    nutrient_values: Dict[str, Optional[float]], 
    serving_size: float,
    ref_serving_size: float,
    is_user_input: bool = False
) -> Dict[str, Optional[float]]:
    """
    Adjust nutrition values from per 100g/ml to the actual serving size,
    and then adjust to reference serving size for foods in list 2.
    
    Args:
        nutrient_values: Dictionary of nutrient values per 100g/ml
        serving_size: The actual serving size specified on the label (g/ml)
        ref_serving_size: Reference serving size from food groups database
        
    Returns:
        Dictionary with adjusted nutrition values
    """
    if serving_size <= 0 or ref_serving_size <= 0:
        return nutrient_values.copy()
    
    # First convert from per 100g/ml to actual serving size
    conversion_factor = serving_size / 100
    
    # Then adjust by reference serving size factor
    reference_factor = ref_serving_size / serving_size
    
    # The total adjustment factor combines both conversions
    adjustment_factor = conversion_factor * reference_factor
    
    # Apply special handling for small reference serving sizes (≤ 30g/ml)
    # Skip doubling if the reference serving size was provided manually by the user
    if ref_serving_size <= 30 and not is_user_input:
        # For small servings, use 2x the reference serving size per regulations
        adjustment_factor = conversion_factor * (2 * ref_serving_size) / serving_size
    
    adjusted_values = {}
    
    for nutrient_key, value in nutrient_values.items():
        if value is not None:
            # Apply the conversion 
            adjusted_value = value * adjustment_factor
            # Round according to nutrient type
            adjusted_values[nutrient_key] = round_nutrition_value(adjusted_value, nutrient_key)
        else:
            adjusted_values[nutrient_key] = None
    
    return adjusted_values

def calculate_rdi_percentage(
    nutrient_value: Optional[float],
    rdi_value: float
) -> Optional[float]:
    """
    Calculate the percentage of RDI for a nutrient.
    
    Args:
        nutrient_value: The value of the nutrient
        rdi_value: The RDI value for the nutrient
        
    Returns:
        The percentage of RDI or None if nutrient_value is None
    """
    if nutrient_value is None or rdi_value <= 0:
        return None
        
    percentage = (nutrient_value / rdi_value) * 100
    # RDI percentage is typically rounded to the nearest whole number
    return round(percentage)

def calculate_per_100kcal(
    nutrient_values: Dict[str, Optional[float]], 
    energy_value: Optional[float]
) -> Dict[str, Optional[float]]:
    """
    Calculate nutrient values per 100kcal for specific nutrients.
    
    Args:
        nutrient_values: Dictionary of nutrient values 
        energy_value: The energy value (kcal)
        
    Returns:
        Dictionary with nutrient values per 100kcal
    """
    if energy_value is None or energy_value <= 0:
        return {}
        
    per_100kcal_factor = 100 / energy_value
    per_100kcal_values = {}
    
    # Calculate for protein and fiber as required by regulations
    for nutrient_key in ["protein", "fiber"]:
        if nutrient_values.get(nutrient_key) is not None:
            per_100kcal_value = nutrient_values[nutrient_key] * per_100kcal_factor
            per_100kcal_values[f"{nutrient_key}_per_100kcal"] = round_nutrition_value(per_100kcal_value, nutrient_key)
    
    return per_100kcal_values

def prepare_rounded_values_display(
    original_values: Dict[str, Optional[float]], 
    serving_size: float = 0, 
    ref_serving_size: float = 0,
    is_in_list_2: bool = False,
    original_input_values: Dict[str, Optional[float]] = None,
    is_from_analysis: bool = False,
    skip_double_small_ref: bool = False
) -> List[Dict[str, Any]]:
    """
    Prepare a display of original and rounded values for nutrition facts.
    
    Args:
        original_values: Dictionary of original nutrient values after adjustments
        serving_size: Serving size on label (g/ml)
        ref_serving_size: Reference serving size from food groups database
        is_in_list_2: Whether the food is in list 2 or not
        original_input_values: Original values input by user (before adjustments)
        is_from_analysis: Whether the values are from analysis results (per 100g/ml)
        
    Returns:
        List of dictionaries containing displayed information about values at different stages
    """
    result = []
    
    # Helper to format values consistently
    def _format_value(val: Optional[float]) -> str:
        if val is None:
            return "-"
        if val < 0:  # negative flags already handled later for rounded, but keep sign here
            return str(val)
        return f"{val:.3f}" if val < 100 else f"{val:.1f}"
    
    # Dictionary to map keys to Thai nutrient names and units
    nutrient_display_info = {
        "energy": {"name": "พลังงาน", "unit": "กิโลแคลอรี่"},
        "fat": {"name": "ไขมันทั้งหมด", "unit": "กรัม"},
        "saturated_fat": {"name": "ไขมันอิ่มตัว", "unit": "กรัม"},
        "trans_fat": {"name": "ไขมันทรานส์", "unit": "กรัม"},
        "cholesterol": {"name": "คอเลสเตอรอล", "unit": "มิลลิกรัม"},
        "protein": {"name": "โปรตีน", "unit": "กรัม"},
        "carbohydrate": {"name": "คาร์โบไฮเดรต", "unit": "กรัม"},
        "fiber": {"name": "ใยอาหาร", "unit": "กรัม"},
        "sugar": {"name": "น้ำตาล", "unit": "กรัม"},
        "sodium": {"name": "โซเดียม", "unit": "มิลลิกรัม"},
        "potassium": {"name": "โพแทสเซียม", "unit": "มิลลิกรัม"}
    }
    
    # For vitamins and minerals, use the key as the name and "µg" or "mg" as the unit
    
    # Process each nutrient
    for key, original_value in original_values.items():
        # Skip None values and derived values (like _per_100kcal)
        if original_value is None or "_per_100kcal" in key or "_rdi_percent" in key:
            continue
            
        # Get nutrient info
        if key in nutrient_display_info:
            nutrient_name = nutrient_display_info[key]["name"]
            unit = nutrient_display_info[key]["unit"]
        else:
            # For vitamins and minerals, use their key as name
            nutrient_name = key
            # Determine unit based on typical vitamin/mineral units
            if key in ["vitamin_a", "vitamin_d", "vitamin_k", "biotin", "folate", 
                      "vitamin_b12", "selenium", "iodine", "molybdenum", "chromium"]:
                unit = "ไมโครกรัม"  # µg
            else:
                unit = "มิลลิกรัม"  # mg
        
        # Capture raw input value (ค่าที่กรอก) if provided by the user
        input_value = None
        if original_input_values and key in original_input_values and original_input_values[key] is not None:
            input_value = original_input_values[key]
        
        # Round the value
        rounded_value = round_nutrition_value(original_value, key)
        
        # Format the original value for display
        original_display = f"{original_value:.3f}" if original_value < 100 else f"{original_value:.1f}"
        
        # Calculate values for serving size and reference serving size
        per_100g_value = None
        per_serving_value = None
        per_ref_serving_value = None
        per_serving_rounded_value = None
        per_ref_serving_rounded_value = None
        
        # If values are from analysis (per 100g/ml), use the original input values directly
        if is_from_analysis and original_input_values and key in original_input_values:
            per_100g_value = original_input_values[key]
            
            # คำนวณค่าต่อหน่วยบริโภคอ้างอิงจากค่าดิบที่ผู้ใช้กรอก (กรณีเป็นค่าวิเคราะห์ต่อ 100g/ml)
            if is_in_list_2 and ref_serving_size > 0:
                multiplier = ref_serving_size / 100
                if ref_serving_size <= 30 and not skip_double_small_ref:
                    multiplier = (ref_serving_size * 2) / 100
                else:
                    multiplier = ref_serving_size / 100
                per_ref_serving_value = per_100g_value * multiplier
                per_ref_serving_rounded_value = round_nutrition_value(per_ref_serving_value, key)
        elif is_in_list_2 and serving_size > 0:
            # Calculate value per 100g (undo the adjustments)
            if ref_serving_size <= 30 and not skip_double_small_ref:
                # For foods with reference serving size <= 30g/ml
                adjustment_factor = serving_size / 100 * (2 * ref_serving_size) / serving_size
                per_100g_value = original_value / adjustment_factor if adjustment_factor != 0 else 0
            else:
                # For foods with reference serving size > 30g/ml
                adjustment_factor = serving_size / 100 * ref_serving_size / serving_size
                per_100g_value = original_value / adjustment_factor if adjustment_factor != 0 else 0
                
            # คำนวณค่าต่อหน่วยบริโภคอ้างอิงจากค่าดิบที่ผู้ใช้กรอก (กรณีเป็นค่าจากฉลากต่อหน่วยบริโภค)
            if original_input_values and key in original_input_values and ref_serving_size > 0:
                # หาอัตราส่วนจากหน่วยบริโภคบนฉลากไปเป็นหน่วยบริโภคอ้างอิง
                if ref_serving_size <= 30 and not skip_double_small_ref:
                    reference_factor = (ref_serving_size * 2) / serving_size
                else:
                    reference_factor = ref_serving_size / serving_size
                per_ref_serving_value = original_input_values[key] * reference_factor
                per_ref_serving_rounded_value = round_nutrition_value(per_ref_serving_value, key)
        
        # For products NOT in list 2, we still want to populate per_serving and reference values
        if not is_in_list_2:
            # per_serving_value comes directly from user input when available (label method)
            if per_serving_value is None and input_value is not None:
                per_serving_value = input_value
                per_serving_rounded_value = round_nutrition_value(per_serving_value, key)
            # Reference value: per 100 g/ml ready-to-eat or derived conversion already present in original_value
            if per_ref_serving_value is None:
                # ใช้ค่า original_value (ซึ่งถูกแปลงเป็นต่อ 100 g/ml พร้อมบริโภคแล้ว) เป็นค่าอ้างอิงหลัก
                per_ref_serving_value = original_value
                per_ref_serving_rounded_value = round_nutrition_value(per_ref_serving_value, key)
        
        # Calculate value per serving size (only if we have per_100g_value)
        if per_100g_value is not None:
            per_serving_value = per_100g_value * serving_size / 100
            
            # Calculate rounded value per serving size
            per_serving_rounded_value = round_nutrition_value(per_serving_value, key)
        
        # Format displays for all numeric columns
        input_value_display = _format_value(input_value)
        per_100g_display = _format_value(per_100g_value)
                           
        per_serving_display = _format_value(per_serving_value)
                              
        # ปรับรูปแบบการแสดงค่าต่อหน่วยบริโภคอ้างอิงให้เหมือนคอลัมน์อื่นๆ
        per_ref_serving_display = _format_value(per_ref_serving_value)
        
        # Format the rounded values for display
        # For serving size rounded value
        if per_serving_rounded_value is not None:
            if per_serving_rounded_value < 0:
                if per_serving_rounded_value == -0.1:  # Trans fat < 0.5
                    per_serving_rounded_display = "น้อยกว่า 0.5"
                elif per_serving_rounded_value == -0.2:  # Cholesterol < 5
                    per_serving_rounded_display = "น้อยกว่า 5"
                elif per_serving_rounded_value == -0.3:  # Protein/Carb/Fiber/Sugar < 1
                    per_serving_rounded_display = "น้อยกว่า 1"
                else:
                    per_serving_rounded_display = str(per_serving_rounded_value)
            else:
                if per_serving_rounded_value == 0:
                    per_serving_rounded_display = "0"
                elif per_serving_rounded_value < 10 and key not in ["energy", "protein", "carbohydrate", "fiber", "sugar"]:
                    per_serving_rounded_display = f"{per_serving_rounded_value:.1f}" if per_serving_rounded_value % 1 != 0 else f"{int(per_serving_rounded_value)}"
                else:
                    per_serving_rounded_display = f"{int(per_serving_rounded_value)}" if per_serving_rounded_value % 1 == 0 else f"{per_serving_rounded_value:.1f}"
        else:
            per_serving_rounded_display = "-"
        
        # For reference serving size rounded value
        if per_ref_serving_rounded_value is not None:
            if per_ref_serving_rounded_value < 0:
                if per_ref_serving_rounded_value == -0.1:  # Trans fat < 0.5
                    per_ref_serving_rounded_display = "น้อยกว่า 0.5"
                elif per_ref_serving_rounded_value == -0.2:  # Cholesterol < 5
                    per_ref_serving_rounded_display = "น้อยกว่า 5"
                elif per_ref_serving_rounded_value == -0.3:  # Protein/Carb/Fiber/Sugar < 1
                    per_ref_serving_rounded_display = "น้อยกว่า 1"
                else:
                    per_ref_serving_rounded_display = str(per_ref_serving_rounded_value)
            else:
                if per_ref_serving_rounded_value == 0:
                    per_ref_serving_rounded_display = "0"
                elif per_ref_serving_rounded_value < 10 and key not in ["energy", "protein", "carbohydrate", "fiber", "sugar"]:
                    per_ref_serving_rounded_display = f"{per_ref_serving_rounded_value:.1f}" if per_ref_serving_rounded_value % 1 != 0 else f"{int(per_ref_serving_rounded_value)}"
                else:
                    per_ref_serving_rounded_display = f"{int(per_ref_serving_rounded_value)}" if per_ref_serving_rounded_value % 1 == 0 else f"{per_ref_serving_rounded_value:.1f}"
        else:
            per_ref_serving_rounded_display = "-"
        
        # For special cases with negative flags
        if rounded_value < 0:
            if rounded_value == -0.1:  # Trans fat < 0.5
                rounded_display = "น้อยกว่า 0.5"
            elif rounded_value == -0.2:  # Cholesterol < 5
                rounded_display = "น้อยกว่า 5"
            elif rounded_value == -0.3:  # Protein/Carb/Fiber/Sugar < 1
                rounded_display = "น้อยกว่า 1"
            else:
                rounded_display = str(rounded_value)
        else:
            if rounded_value == 0:
                rounded_display = "0"
            elif rounded_value < 10 and key not in ["energy", "protein", "carbohydrate", "fiber", "sugar"]:
                # For small values (but not energy, protein, carbs, fiber, sugar which are shown as integers)
                rounded_display = f"{rounded_value:.1f}" if rounded_value % 1 != 0 else f"{int(rounded_value)}"
            else:
                rounded_display = f"{int(rounded_value)}" if rounded_value % 1 == 0 else f"{rounded_value:.1f}"
        
        # Add to result
        result.append({
            "nutrient": nutrient_name,
            "input_value": input_value_display,
            "per_100g": per_100g_display,
            "per_serving": per_serving_display,
            "per_serving_rounded": per_serving_rounded_display,
            "per_ref_serving": per_ref_serving_display,
            "per_ref_serving_rounded": per_ref_serving_rounded_display,
            "rounded": rounded_display,
            "unit": unit,
            "key": key
        })
    
    return result