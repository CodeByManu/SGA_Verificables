from datetime import datetime, date
from typing import Optional, Union, Any
import re

class FormValidationError(Exception):
    """Excepción específica para errores de validación de formularios"""
    pass

def validate_required_string(value: Any, field_name: str) -> str:

    if value is None:
        raise FormValidationError(f"{field_name} es requerido")
    
    if not isinstance(value, str):
        raise FormValidationError(f"{field_name} debe ser texto")
    
    cleaned_value = value.strip()
    if not cleaned_value:
        raise FormValidationError(f"{field_name} no puede estar vacío")
    
    return cleaned_value

def validate_optional_string(value: Any, field_name: str) -> Optional[str]:

    if value is None or value == "":
        return None
    
    if not isinstance(value, str):
        raise FormValidationError(f"{field_name} debe ser texto")
    
    cleaned_value = value.strip()
    return cleaned_value if cleaned_value else None

def validate_integer(value: Any, field_name: str, min_val: Optional[int] = None, 
                    max_val: Optional[int] = None, required: bool = True) -> Optional[int]:

    if value is None or value == "":
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            if required:
                raise FormValidationError(f"{field_name} es requerido")
            return None
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise FormValidationError(f"{field_name} debe ser un número entero válido")
    
    if min_val is not None and int_value < min_val:
        raise FormValidationError(f"{field_name} debe ser mayor o igual a {min_val}")
    
    if max_val is not None and int_value > max_val:
        raise FormValidationError(f"{field_name} debe ser menor o igual a {max_val}")
    
    return int_value

def validate_float(value: Any, field_name: str, min_val: Optional[float] = None,
                  max_val: Optional[float] = None, required: bool = True) -> Optional[float]:

    if value is None or value == "":
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            if required:
                raise FormValidationError(f"{field_name} es requerido")
            return None
    
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise FormValidationError(f"{field_name} debe ser un número válido")
    
    if min_val is not None and float_value < min_val:
        raise FormValidationError(f"{field_name} debe ser mayor o igual a {min_val}")
    
    if max_val is not None and float_value > max_val:
        raise FormValidationError(f"{field_name} debe ser menor o igual a {max_val}")
    
    return float_value

def validate_date(value: Any, field_name: str, required: bool = True,
                 date_formats: list = None) -> Optional[date]:

    if date_formats is None:
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    
    if value is None or value == "":
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    if not isinstance(value, str):
        raise FormValidationError(f"{field_name} debe ser una fecha válida")
    
    date_str = value.strip()
    if not date_str:
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, date_format).date()
            break
        except ValueError:
            continue
    
    if parsed_date is None:
        formats_str = ", ".join(date_formats)
        raise FormValidationError(f"{field_name} debe tener formato válido ({formats_str})")
    
    return parsed_date

def validate_email_format(value: Any, field_name: str, required: bool = True) -> Optional[str]:

    if value is None or value == "":
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    if not isinstance(value, str):
        raise FormValidationError(f"{field_name} debe ser texto")
    
    email = value.strip().lower()
    if not email:
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise FormValidationError(f"{field_name} debe tener un formato válido")
    
    if len(email) > 254:
        raise FormValidationError(f"{field_name} es demasiado largo")
    
    return email

def validate_id_parameter(value: Any, field_name: str) -> int:

    if not isinstance(value, int):
        raise FormValidationError(f"{field_name} debe ser un número entero")
    
    if value <= 0:
        raise FormValidationError(f"{field_name} debe ser mayor a 0")
    
    if value > 2147483647:
        raise FormValidationError(f"{field_name} es demasiado grande")
    
    return value

def validate_float(value: Any, field_name: str, min_val: Optional[float] = None,
                  max_val: Optional[float] = None, required: bool = True, 
                  decimal_places: Optional[int] = None) -> Optional[float]:
    
    
    if value is None or value == "":
        if required:
            raise FormValidationError(f"{field_name} es requerido")
        return None
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            if required:
                raise FormValidationError(f"{field_name} es requerido")
            return None
        
        value = value.replace(',', '.')
    
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise FormValidationError(f"{field_name} debe ser un número válido")
    
    if not isinstance(float_value, (int, float)) or float_value != float_value:
        raise FormValidationError(f"{field_name} debe ser un número válido")
    
    if float_value == float('inf') or float_value == float('-inf'):
        raise FormValidationError(f"{field_name} debe ser un número finito")
    
    if min_val is not None and float_value < min_val:
        raise FormValidationError(f"{field_name} debe ser mayor o igual a {min_val}")
    
    if max_val is not None and float_value > max_val:
        raise FormValidationError(f"{field_name} debe ser menor o igual a {max_val}")
    
    if decimal_places is not None:
        str_value = str(float_value)
        if '.' in str_value:
            decimals = len(str_value.split('.')[1])
            if decimals > decimal_places:
                raise FormValidationError(f"{field_name} no puede tener más de {decimal_places} decimales")
    
    return float_value

def validate_period_format(period_string: str, field_name: str = "período") -> str:

    if not period_string:
        raise FormValidationError(f"{field_name} es requerido")
    
    if not isinstance(period_string, str):
        raise FormValidationError(f"{field_name} debe ser texto")
        
    period = period_string.strip()
    if not period:
        raise FormValidationError(f"{field_name} no puede estar vacío")

    pattern = r'^(\d{4})-([12])$'
    match = re.match(pattern, period)
    
    if not match:
        raise FormValidationError(
            f"{field_name} debe tener formato YYYY-S (ejemplo: 2025-1 o 2025-2)"
        )
    
    year_str, semester_str = match.groups()
    year = int(year_str)
    semester = int(semester_str)

    current_year = datetime.now().year
    min_year = current_year - 10 
    max_year = current_year + 5 
    
    if year < min_year:
        raise FormValidationError(
            f"{field_name} no puede ser anterior al año {min_year}"
        )
    
    if year > max_year:
        raise FormValidationError(
            f"{field_name} no puede ser posterior al año {max_year}"
        )

    if semester not in [1, 2]:
        raise FormValidationError(
            f"{field_name} debe tener semestre válido (1 o 2)"
        )
    
    return period

def validate_course_code(value: str, field_name: str = "código de curso") -> str:

    if not value:
        raise FormValidationError(f"{field_name} es requerido")
    
    if not isinstance(value, str):
        raise FormValidationError(f"{field_name} debe ser texto")

    code = value.strip().upper()
    if not code:
        raise FormValidationError(f"{field_name} no puede estar vacío")
    
    pattern = r'^([A-Z]{3})(-\d{3}|\d{4})$'
    match = re.match(pattern, code)
    
    if not match:
        raise FormValidationError(
            f"{field_name} debe tener formato XXX-NNN o XXXNNNN (3 letras, guión + 3 números o 4 números). Ejemplo: ICC-103 o ICC1234"
        )
    
    letters, numbers_part = match.groups()
    
    if numbers_part.startswith('-'):
        numbers = numbers_part[1:]
    else:
        numbers = numbers_part
    
    if len(set(letters)) == 1:
        raise FormValidationError(
            f"{field_name} no puede tener las mismas 3 letras repetidas"
        )
    
    if numbers == "000":
        raise FormValidationError(
            f"{field_name} no puede terminar en 000"
        )
    
    number_value = int(numbers)
    if number_value < 1:
        raise FormValidationError(
            f"{field_name} debe tener números mayores a 0"
        )
    
    return code

