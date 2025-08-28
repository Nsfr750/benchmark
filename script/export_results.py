"""
Result export functionality for the Benchmark application.
Handles exporting benchmark results to various formats.
"""
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class ResultExporter:
    """Handles exporting benchmark results to different file formats."""
    
    @staticmethod
    def export_to_json(data: Union[Dict, List], file_path: str) -> bool:
        """Export data to a JSON file.
        
        Args:
            data: Data to export (must be JSON-serializable)
            file_path: Path to save the JSON file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict], file_path: str) -> bool:
        """Export data to a CSV file.
        
        Args:
            data: List of dictionaries to export
            file_path: Path to save the CSV file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not data:
            return False
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Get all possible fieldnames from all dictionaries
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
                
            # Flatten nested dictionaries
            flattened_data = []
            for item in data:
                flat_item = {}
                for key, value in item.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flat_item[f"{key}_{subkey}"] = subvalue
                    else:
                        flat_item[key] = value
                flattened_data.append(flat_item)
            
            # Update fieldnames for flattened data
            fieldnames = set()
            for item in flattened_data:
                fieldnames.update(item.keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(flattened_data)
                
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_results(
        results: Union[Dict, List], 
        output_dir: str = "results",
        base_filename: str = "benchmark_results",
        formats: List[str] = None
    ) -> Dict[str, str]:
        """Export results to multiple formats.
        
        Args:
            results: Results data to export
            output_dir: Directory to save the exported files
            base_filename: Base filename (without extension)
            formats: List of formats to export ('json', 'csv')
            
        Returns:
            Dict with format as key and file path as value
        """
        if formats is None:
            formats = ['json', 'csv']
            
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure results is a list for consistent processing
        results_list = results if isinstance(results, list) else [results]
        
        for fmt in formats:
            if fmt.lower() == 'json':
                filename = f"{base_filename}_{timestamp}.json"
                filepath = os.path.join(output_dir, filename)
                if ResultExporter.export_to_json(results_list, filepath):
                    exported_files['json'] = filepath
                    
            elif fmt.lower() == 'csv':
                # For CSV, we need to ensure we have a list of flat dictionaries
                flat_results = []
                for result in results_list:
                    flat_result = {}
                    for key, value in result.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                flat_result[f"{key}_{subkey}"] = subvalue
                        else:
                            flat_result[key] = value
                    flat_results.append(flat_result)
                
                filename = f"{base_filename}_{timestamp}.csv"
                filepath = os.path.join(output_dir, filename)
                if ResultExporter.export_to_csv(flat_results, filepath):
                    exported_files['csv'] = filepath
        
        return exported_files

def get_export_formats() -> List[Dict[str, str]]:
    """Get available export formats with descriptions."""
    return [
        {"id": "json", "name": "JSON", "description": "JavaScript Object Notation (human-readable)"},
        {"id": "csv", "name": "CSV", "description": "Comma-Separated Values (spreadsheet-friendly)"},
    ]
