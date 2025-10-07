"""CSV file loader."""

import csv
from typing import List, Dict
from .base import BaseLoader


class CSVLoader(BaseLoader):
    """Load content from CSV files."""
    
    def __init__(self, include_headers: bool = True):
        """
        Initialize CSV loader.
        
        Args:
            include_headers: Whether to include column headers in output
        """
        self.include_headers = include_headers
    
    def load(self, filepath: str) -> List[Dict[str, str]]:
        """
        Load and format CSV data as text.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List containing a single document dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if not rows:
                raise ValueError("CSV file is empty")
            
            # Format CSV as readable text
            text_lines = []
            
            if self.include_headers and len(rows) > 0:
                headers = rows[0]
                data_rows = rows[1:]
                
                # Create text representation
                text_lines.append(f"CSV Data with {len(data_rows)} rows and {len(headers)} columns:")
                text_lines.append(f"Columns: {', '.join(headers)}")
                text_lines.append("")
                
                for i, row in enumerate(data_rows):
                    row_text = " | ".join([f"{headers[j]}: {val}" for j, val in enumerate(row) if j < len(headers)])
                    text_lines.append(f"Row {i+1}: {row_text}")
            else:
                # No headers, just format rows
                text_lines.append(f"CSV Data with {len(rows)} rows:")
                for i, row in enumerate(rows):
                    text_lines.append(f"Row {i+1}: {' | '.join(row)}")
            
            text = '\n'.join(text_lines)
            
            return [{
                'content': text,
                'source': filepath,
                'type': 'csv'
            }]
            
        except Exception as e:
            raise ValueError(f"Error loading CSV {filepath}: {str(e)}")
