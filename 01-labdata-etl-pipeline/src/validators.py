"""
Chemistry-aware validation module for pharmaceutical data
Author: MSc Chemistry → Data Engineer
"""

from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PharmaceuticalValidator:
    """Domain-specific validators for pharmaceutical laboratory data"""
    
    # Chemistry constants
    VALID_PH_RANGE = (0.0, 14.0)
    CONCENTRATION_UNITS = ['mg/mL', 'µM', 'mM', 'g/L', 'M']
    TEMP_RANGES = {
        'celsius': (-273.15, 1000),
        'fahrenheit': (-459.67, 1832),
        'kelvin': (0, 1273.15)
    }
    
    @staticmethod
    def validate_ph(ph_value: float) -> Tuple[bool, str]:
        """
        Validate pH value within chemistry-valid range
        
        Args:
            ph_value: pH measurement
            
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(ph_value, (int, float)):
            return False, f"pH must be numeric, got {type(ph_value)}"
        
        min_ph, max_ph = PharmaceuticalValidator.VALID_PH_RANGE
        if min_ph <= ph_value <= max_ph:
            return True, ""
        
        return False, f"pH {ph_value} out of valid range {PharmaceuticalValidator.VALID_PH_RANGE}"
    
    @staticmethod
    def convert_concentration(
        value: float, 
        from_unit: str, 
        to_unit: str = 'mM',
        molecular_weight: Optional[float] = None
    ) -> float:
        """
        Convert between concentration units
        
        Args:
            value: Concentration value
            from_unit: Source unit (mg/mL, µM, mM, g/L)
            to_unit: Target unit (default: mM)
            molecular_weight: Required for mass/molar conversions
            
        Returns:
            Converted concentration value
        """
        # Conversion factors to mM (base unit)
        to_mM = {
            'mM': 1.0,
            'µM': 0.001,
            'M': 1000.0,
            'mg/mL': lambda mw: 1000.0 / mw if mw else None,
            'g/L': lambda mw: 1000.0 / mw if mw else None
        }
        
        # Convert to mM first
        if callable(to_mM[from_unit]):
            if molecular_weight is None:
                raise ValueError(f"Molecular weight required for {from_unit} conversion")
            base_value = value * to_mM[from_unit](molecular_weight)
        else:
            base_value = value * to_mM[from_unit]
        
        # Convert from mM to target unit
        if callable(to_mM[to_unit]):
            if molecular_weight is None:
                raise ValueError(f"Molecular weight required for {to_unit} conversion")
            return base_value / (to_mM[to_unit](molecular_weight))
        
        return base_value / to_mM[to_unit]
    
    @staticmethod
    def validate_temperature(
        temp: float, 
        unit: str = 'celsius'
    ) -> Tuple[bool, str]:
        """
        Validate temperature within physical constraints
        
        Args:
            temp: Temperature value
            unit: Temperature unit (celsius/fahrenheit/kelvin)
            
        Returns:
            (is_valid, error_message)
        """
        unit = unit.lower()
        
        if unit not in PharmaceuticalValidator.TEMP_RANGES:
            return False, f"Unknown temperature unit: {unit}"
        
        min_temp, max_temp = PharmaceuticalValidator.TEMP_RANGES[unit]
        
        if min_temp <= temp <= max_temp:
            return True, ""
        
        return False, f"Temperature {temp}°{unit[0].upper()} out of valid range ({min_temp}, {max_temp})"
    
    @staticmethod
    def validate_experiment_data(data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate complete experiment record
        
        Args:
            data: Dictionary with experiment fields
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ['experiment_id', 'compound_name', 'ph', 'temperature']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # pH validation
        is_valid, error = PharmaceuticalValidator.validate_ph(data['ph'])
        if not is_valid:
            errors.append(error)
        
        # Temperature validation
        is_valid, error = PharmaceuticalValidator.validate_temperature(
            data.get('temperature', 0), 
            data.get('temp_unit', 'celsius')
        )
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors


def generate_quality_report(
    total_records: int,
    valid_records: int,
    errors: List[str]
) -> str:
    """
    Generate data quality summary report
    
    Args:
        total_records: Total records processed
        valid_records: Records passing validation
        errors: List of validation errors
        
    Returns:
        Formatted quality report string
    """
    pass_rate = (valid_records / total_records * 100) if total_records > 0 else 0
    
    report = f"""
    ╔════════════════════════════════════════╗
    ║     DATA QUALITY REPORT                ║
    ╠════════════════════════════════════════╣
    ║ Total Records:     {total_records:>6}            ║
    ║ Valid Records:     {valid_records:>6}            ║
    ║ Failed Records:    {total_records - valid_records:>6}            ║
    ║ Pass Rate:         {pass_rate:>5.1f}%           ║
    ╚════════════════════════════════════════╝
    """
    
    if errors:
        report += f"\n\nTop Validation Errors:\n"
        for i, error in enumerate(errors[:5], 1):
            report += f"  {i}. {error}\n"
    
    return report


# Example usage
if __name__ == "__main__":
    # Test pH validation
    test_cases = [7.4, 0.5, 14.0, -1.0, 15.5]
    
    print("pH Validation Tests:")
    for ph in test_cases:
        is_valid, msg = PharmaceuticalValidator.validate_ph(ph)
        status = "✓" if is_valid else "✗"
        print(f"  {status} pH {ph}: {msg if msg else 'VALID'}")
    
    # Test concentration conversion
    print("\nConcentration Conversion Test:")
    result = PharmaceuticalValidator.convert_concentration(
        value=100,
        from_unit='µM',
        to_unit='mM'
    )
    print(f"  100 µM = {result} mM")
    
    # Test full record validation
    print("\nExperiment Record Validation:")
    test_record = {
        'experiment_id': 'EXP001',
        'compound_name': 'Aspirin',
        'ph': 7.4,
        'temperature': 25,
        'temp_unit': 'celsius'
    }
    
    is_valid, errors = PharmaceuticalValidator.validate_experiment_data(test_record)
    print(f"  Record valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
            