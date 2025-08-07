#!/usr/bin/env python3
"""
Data Cleaner Module for YAZAKI Component Processing System
Comprehensive data cleaning before processing
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DataCleaner:
    """Comprehensive data cleaning for component data"""
    
    def __init__(self):
        self.cleaning_stats = {}
        self.cleaning_log = []
    
    def clean_dataframe(self, df: pd.DataFrame, options: Dict[str, bool] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean a DataFrame with comprehensive cleaning options
        
        Args:
            df: Input DataFrame
            options: Cleaning options dictionary
            
        Returns:
            (cleaned_dataframe, cleaning_stats)
        """
        if options is None:
            options = self.get_default_cleaning_options()
        
        logger.info(f"Starting data cleaning with {len(df)} rows and {len(df.columns)} columns")
        
        # Initialize stats
        self.cleaning_stats = {
            'original_rows': len(df),
            'original_columns': len(df.columns),
            'operations_performed': [],
            'issues_found': [],
            'issues_fixed': []
        }
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # 1. Remove completely empty rows
        if options.get('remove_empty_rows', True):
            cleaned_df = self._remove_empty_rows(cleaned_df)
        
        # 2. Remove completely empty columns
        if options.get('remove_empty_columns', True):
            cleaned_df = self._remove_empty_columns(cleaned_df)
        
        # 3. Clean column names
        if options.get('clean_column_names', True):
            cleaned_df = self._clean_column_names(cleaned_df)
        
        # 4. Standardize PN format
        if options.get('standardize_pn', True):
            cleaned_df = self._standardize_part_numbers(cleaned_df)
        
        # 5. Remove duplicate rows
        if options.get('remove_duplicates', True):
            cleaned_df = self._remove_duplicates(cleaned_df)
        
        # 6. Clean whitespace
        if options.get('clean_whitespace', True):
            cleaned_df = self._clean_whitespace(cleaned_df)
        
        # 7. Standardize text case
        if options.get('standardize_case', True):
            cleaned_df = self._standardize_text_case(cleaned_df)
        
        # 8. Fix data types
        if options.get('fix_data_types', True):
            cleaned_df = self._fix_data_types(cleaned_df)
        
        # 9. Handle missing values
        if options.get('handle_missing', True):
            cleaned_df = self._handle_missing_values(cleaned_df)
        
        # 10. Validate data integrity
        if options.get('validate_data', True):
            cleaned_df = self._validate_data_integrity(cleaned_df)
        
        # Final stats
        self.cleaning_stats.update({
            'final_rows': len(cleaned_df),
            'final_columns': len(cleaned_df.columns),
            'rows_removed': self.cleaning_stats['original_rows'] - len(cleaned_df),
            'columns_removed': self.cleaning_stats['original_columns'] - len(cleaned_df.columns)
        })
        
        logger.info(f"Data cleaning completed: {len(cleaned_df)} rows, {len(cleaned_df.columns)} columns")
        
        return cleaned_df, self.cleaning_stats
    
    def _remove_empty_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove completely empty rows"""
        initial_rows = len(df)
        df_cleaned = df.dropna(how='all')
        removed_rows = initial_rows - len(df_cleaned)
        
        if removed_rows > 0:
            self.cleaning_stats['operations_performed'].append(f"Removed {removed_rows} empty rows")
            self.cleaning_stats['issues_found'].append(f"Found {removed_rows} completely empty rows")
            self.cleaning_stats['issues_fixed'].append(f"Removed {removed_rows} empty rows")
        
        return df_cleaned
    
    def _remove_empty_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove completely empty columns"""
        initial_cols = len(df.columns)
        df_cleaned = df.dropna(axis=1, how='all')
        removed_cols = initial_cols - len(df_cleaned.columns)
        
        if removed_cols > 0:
            self.cleaning_stats['operations_performed'].append(f"Removed {removed_cols} empty columns")
            self.cleaning_stats['issues_found'].append(f"Found {removed_cols} completely empty columns")
            self.cleaning_stats['issues_fixed'].append(f"Removed {removed_cols} empty columns")
        
        return df_cleaned
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column names"""
        original_columns = df.columns.tolist()
        
        # Clean column names
        new_columns = []
        for col in df.columns:
            # Convert to string and strip whitespace
            clean_col = str(col).strip()
            
            # Remove extra whitespace
            clean_col = re.sub(r'\s+', ' ', clean_col)
            
            # Remove special characters at start/end
            clean_col = re.sub(r'^[^\w]+|[^\w]+$', '', clean_col)
            
            new_columns.append(clean_col)
        
        df.columns = new_columns
        
        # Check for changes
        changes = sum(1 for old, new in zip(original_columns, new_columns) if old != new)
        if changes > 0:
            self.cleaning_stats['operations_performed'].append(f"Cleaned {changes} column names")
            self.cleaning_stats['issues_found'].append(f"Found {changes} columns with formatting issues")
            self.cleaning_stats['issues_fixed'].append(f"Standardized {changes} column names")
        
        return df
    
    def _standardize_part_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize part number format"""
        pn_columns = self._find_pn_columns(df)
        
        for col in pn_columns:
            if col in df.columns:
                original_values = df[col].copy()
                
                # Clean PN values
                df[col] = df[col].astype(str)
                df[col] = df[col].str.strip()
                df[col] = df[col].str.upper()
                df[col] = df[col].replace('NAN', np.nan)
                df[col] = df[col].replace('', np.nan)
                
                # Count changes
                changes = sum(1 for old, new in zip(original_values, df[col]) 
                             if pd.notna(old) and pd.notna(new) and str(old) != str(new))
                
                if changes > 0:
                    self.cleaning_stats['operations_performed'].append(f"Standardized {changes} part numbers in {col}")
                    self.cleaning_stats['issues_fixed'].append(f"Cleaned {changes} part numbers")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial_rows = len(df)
        df_cleaned = df.drop_duplicates()
        removed_rows = initial_rows - len(df_cleaned)
        
        if removed_rows > 0:
            self.cleaning_stats['operations_performed'].append(f"Removed {removed_rows} duplicate rows")
            self.cleaning_stats['issues_found'].append(f"Found {removed_rows} duplicate rows")
            self.cleaning_stats['issues_fixed'].append(f"Removed {removed_rows} duplicates")
        
        return df_cleaned
    
    def _clean_whitespace(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean whitespace in text columns"""
        text_columns = df.select_dtypes(include=['object']).columns
        changes_count = 0
        
        for col in text_columns:
            original_values = df[col].copy()
            
            # Clean whitespace
            df[col] = df[col].astype(str)
            df[col] = df[col].str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            df[col] = df[col].replace('nan', np.nan)
            
            # Count changes
            changes = sum(1 for old, new in zip(original_values, df[col]) 
                         if pd.notna(old) and str(old) != str(new))
            changes_count += changes
        
        if changes_count > 0:
            self.cleaning_stats['operations_performed'].append(f"Cleaned whitespace in {len(text_columns)} columns")
            self.cleaning_stats['issues_fixed'].append(f"Fixed {changes_count} whitespace issues")
        
        return df
    
    def _standardize_text_case(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize text case for specific columns"""
        # Find columns that should be uppercase (like PN, Status)
        uppercase_patterns = ['pn', 'part', 'status', 'state']
        changes_count = 0
        
        for col in df.columns:
            col_lower = col.lower()
            if any(pattern in col_lower for pattern in uppercase_patterns):
                if df[col].dtype == 'object':
                    original_values = df[col].copy()
                    df[col] = df[col].str.upper()
                    
                    changes = sum(1 for old, new in zip(original_values, df[col]) 
                                 if pd.notna(old) and str(old) != str(new))
                    changes_count += changes
        
        if changes_count > 0:
            self.cleaning_stats['operations_performed'].append(f"Standardized text case")
            self.cleaning_stats['issues_fixed'].append(f"Fixed {changes_count} case issues")
        
        return df
    
    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix data types where possible"""
        changes_count = 0
        
        for col in df.columns:
            original_dtype = df[col].dtype
            
            # Try to convert numeric columns
            if df[col].dtype == 'object':
                # Check if it's numeric
                try:
                    # Remove common non-numeric characters
                    test_series = df[col].str.replace(r'[,$%]', '', regex=True)
                    pd.to_numeric(test_series, errors='raise')
                    
                    # If successful, convert
                    df[col] = pd.to_numeric(df[col].str.replace(r'[,$%]', '', regex=True), errors='coerce')
                    changes_count += 1
                    
                except (ValueError, AttributeError):
                    pass
        
        if changes_count > 0:
            self.cleaning_stats['operations_performed'].append(f"Fixed data types for {changes_count} columns")
            self.cleaning_stats['issues_fixed'].append(f"Converted {changes_count} columns to proper types")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        missing_stats = df.isnull().sum()
        total_missing = missing_stats.sum()
        
        if total_missing > 0:
            self.cleaning_stats['operations_performed'].append(f"Analyzed {total_missing} missing values")
            self.cleaning_stats['issues_found'].append(f"Found {total_missing} missing values across {len(missing_stats[missing_stats > 0])} columns")
            
            # Log missing value statistics
            for col, count in missing_stats.items():
                if count > 0:
                    percentage = (count / len(df)) * 100
                    self.cleaning_log.append(f"Column '{col}': {count} missing values ({percentage:.1f}%)")
        
        return df
    
    def _validate_data_integrity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data integrity"""
        validation_issues = []
        
        # Check for PN columns
        pn_columns = self._find_pn_columns(df)
        if not pn_columns:
            validation_issues.append("No Part Number column found")
        
        # Check for extremely long values
        for col in df.select_dtypes(include=['object']).columns:
            max_length = df[col].str.len().max()
            if pd.notna(max_length) and max_length > 1000:
                validation_issues.append(f"Column '{col}' has extremely long values (max: {max_length} chars)")
        
        if validation_issues:
            self.cleaning_stats['issues_found'].extend(validation_issues)
        
        return df
    
    def _find_pn_columns(self, df: pd.DataFrame) -> List[str]:
        """Find Part Number columns"""
        pn_patterns = ['pn', 'part number', 'part_number', 'yazaki pn', 'yazaki_pn']
        pn_columns = []
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(pattern in col_lower for pattern in pn_patterns):
                pn_columns.append(col)
        
        return pn_columns
    
    def get_default_cleaning_options(self) -> Dict[str, bool]:
        """Get default cleaning options"""
        return {
            'remove_empty_rows': True,
            'remove_empty_columns': True,
            'clean_column_names': True,
            'standardize_pn': True,
            'remove_duplicates': True,
            'clean_whitespace': True,
            'standardize_case': True,
            'fix_data_types': True,
            'handle_missing': True,
            'validate_data': True
        }
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get comprehensive cleaning report"""
        return {
            'stats': self.cleaning_stats,
            'log': self.cleaning_log,
            'summary': {
                'total_operations': len(self.cleaning_stats.get('operations_performed', [])),
                'issues_found': len(self.cleaning_stats.get('issues_found', [])),
                'issues_fixed': len(self.cleaning_stats.get('issues_fixed', [])),
                'data_quality_improvement': self._calculate_quality_improvement()
            }
        }
    
    def _calculate_quality_improvement(self) -> str:
        """Calculate data quality improvement percentage"""
        original_rows = self.cleaning_stats.get('original_rows', 0)
        final_rows = self.cleaning_stats.get('final_rows', 0)
        
        if original_rows == 0:
            return "0%"
        
        # Simple quality metric based on data reduction and fixes
        issues_fixed = len(self.cleaning_stats.get('issues_fixed', []))
        if issues_fixed == 0:
            return "No issues found"
        
        # Calculate improvement based on issues fixed vs data size
        improvement = min(100, (issues_fixed / original_rows) * 100)
        return f"{improvement:.1f}%"

# Convenience function
def clean_data(df: pd.DataFrame, options: Dict[str, bool] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convenience function to clean data
    
    Args:
        df: Input DataFrame
        options: Cleaning options
        
    Returns:
        (cleaned_dataframe, cleaning_report)
    """
    cleaner = DataCleaner()
    cleaned_df, stats = cleaner.clean_dataframe(df, options)
    report = cleaner.get_cleaning_report()
    
    return cleaned_df, report
