"""
Universal alias mapping system for natural language queries
Loads all alias configurations from JSON files for better maintainability
"""
import json
import os
from typing import Dict, List, Set, Optional, Any
from pathlib import Path


class UniversalAliasMapper:
    """Universal alias mapper that loads configurations from JSON files"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the alias mapper with configuration from JSON file
        
        Args:
            config_path: Path to the aliases.json file. If None, uses default fixture path.
        """
        if config_path is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / "fixture" / "aliases.json"
        
        self.config_path = Path(config_path)
        self.aliases_config = {}
        self.product_to_aliases = {}
        
        # Load configuration
        self._load_aliases_config()
        self._build_reverse_mappings()
    
    def _load_aliases_config(self):
        """Load alias configuration from JSON file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Aliases config file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.aliases_config = json.load(f)
            
            print(f"✅ Loaded aliases config from: {self.config_path}")
            
            # Validate required sections
            required_sections = ['product_aliases', 'os_aliases', 'http_method_aliases']
            for section in required_sections:
                if section not in self.aliases_config:
                    print(f"⚠️ Warning: Missing section '{section}' in aliases config")
                    
        except Exception as e:
            print(f"❌ Error loading aliases config: {e}")
            # Fallback to empty config
            self.aliases_config = {
                'product_aliases': {},
                'os_aliases': {},
                'http_method_aliases': {},
                'provider_aliases': {},
                'resource_aliases': {},
                'time_aliases': {},
                'quantity_aliases': {},
                'comparison_aliases': {}
            }
    
    def _build_reverse_mappings(self):
        """Build reverse mappings for fast lookup (product -> aliases)"""
        product_aliases = self.aliases_config.get('product_aliases', {})
        
        for alias, products in product_aliases.items():
            for product in products:
                if product not in self.product_to_aliases:
                    self.product_to_aliases[product] = set()
                self.product_to_aliases[product].add(alias)
    
    def get_aliases_for_category(self, category: str) -> Dict[str, List[str]]:
        """
        Get all aliases for a specific category
        
        Args:
            category: Category name (e.g., 'product_aliases', 'os_aliases')
            
        Returns:
            Dictionary of alias -> target mappings
        """
        return self.aliases_config.get(category, {})
    
    def find_products_by_query(self, query_text: str, available_products: List[str]) -> List[str]:
        """
        Find products that match the query text using aliases or direct names
        
        Args:
            query_text: User query text
            available_products: List of available product names from schema
            
        Returns:
            List of matching product names
        """
        query_lower = query_text.lower()
        matched_products = set()
        
        # First check for direct product name matches
        for product in available_products:
            if product.lower() in query_lower:
                matched_products.add(product)
        
        # If no direct matches, check aliases
        if not matched_products:
            product_aliases = self.get_aliases_for_category('product_aliases')
            for alias, products in product_aliases.items():
                if alias.lower() in query_lower:
                    # Only add products that are actually available in the schema
                    for product in products:
                        if product in available_products:
                            matched_products.add(product)
        
        return list(matched_products)
    
    def find_matches_by_category(self, query_text: str, category: str, available_values: Optional[List[str]] = None) -> List[str]:
        """
        Find matches in a specific category
        
        Args:
            query_text: User query text
            category: Category to search in (e.g., 'os_aliases', 'http_method_aliases')
            available_values: Optional list of available values to filter against
            
        Returns:
            List of matching values
        """
        query_lower = query_text.lower()
        matched_values = set()
        
        category_aliases = self.get_aliases_for_category(category)
        
        for alias, targets in category_aliases.items():
            if alias.lower() in query_lower:
                for target in targets:
                    if available_values is None or target in available_values:
                        matched_values.add(target)
        
        return list(matched_values)
    
    def get_aliases_for_product(self, product_name: str) -> Set[str]:
        """Get all aliases for a given product name"""
        return self.product_to_aliases.get(product_name, set())
    
    def get_all_aliases(self) -> Dict[str, Dict]:
        """Get all alias mappings"""
        return {
            key: value for key, value in self.aliases_config.items() 
            if not key.startswith('_')  # Exclude metadata
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata"""
        return self.aliases_config.get('_metadata', {})
    
    def add_alias(self, category: str, alias: str, targets: List[str], save_to_file: bool = False):
        """
        Add a new alias mapping
        
        Args:
            category: Category to add to (e.g., 'product_aliases')
            alias: The alias term
            targets: List of target values
            save_to_file: Whether to save changes back to JSON file
        """
        if category not in self.aliases_config:
            self.aliases_config[category] = {}
        
        self.aliases_config[category][alias.lower()] = targets
        
        # Update reverse mapping for products
        if category == 'product_aliases':
            for target in targets:
                if target not in self.product_to_aliases:
                    self.product_to_aliases[target] = set()
                self.product_to_aliases[target].add(alias.lower())
        
        if save_to_file:
            self.save_config()
    
    def save_config(self):
        """Save current configuration back to JSON file"""
        try:
            # Update metadata
            if '_metadata' not in self.aliases_config:
                self.aliases_config['_metadata'] = {}
            
            self.aliases_config['_metadata']['last_updated'] = "2025-08-28"
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.aliases_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved aliases config to: {self.config_path}")
            
        except Exception as e:
            print(f"❌ Error saving aliases config: {e}")
    
    def get_enhanced_column_info(self, column_name: str, column_metadata: Dict) -> Dict[str, Any]:
        """
        Get enhanced column information with relevant aliases
        
        Args:
            column_name: Name of the column
            column_metadata: Existing column metadata
            
        Returns:
            Enhanced column information with aliases
        """
        enhanced_info = column_metadata.copy()
        
        # Add alias information based on column type
        if column_name == 'Product' and column_metadata.get('enum'):
            product_aliases = {}
            for product in column_metadata.get('enum', []):
                aliases = list(self.get_aliases_for_product(product))
                if aliases:
                    product_aliases[product] = aliases
            
            if product_aliases:
                enhanced_info['product_aliases'] = product_aliases
                enhanced_info['alias_examples'] = self._generate_alias_examples(product_aliases)
        
        elif column_name == 'OS':
            os_aliases = self.get_aliases_for_category('os_aliases')
            if os_aliases:
                enhanced_info['common_aliases'] = {
                    target[0]: alias_key for alias_key, target in os_aliases.items() 
                    if target and len(target) > 0
                }
        
        elif column_name == 'HttpMethod':
            http_aliases = self.get_aliases_for_category('http_method_aliases')
            if http_aliases:
                enhanced_info['common_aliases'] = {
                    target[0]: alias_key for alias_key, target in http_aliases.items() 
                    if target and len(target) > 0
                }
        
        elif column_name == 'Provider':
            provider_aliases = self.get_aliases_for_category('provider_aliases')
            enhanced_info['common_patterns'] = {
                alias_key: f"{', '.join(targets)}" 
                for alias_key, targets in provider_aliases.items()
            }
        
        elif column_name == 'Resource':
            resource_aliases = self.get_aliases_for_category('resource_aliases')
            enhanced_info['common_patterns'] = {
                alias_key: f"{', '.join(targets)}" 
                for alias_key, targets in resource_aliases.items()
            }
        
        return enhanced_info
    
    def _generate_alias_examples(self, product_aliases: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate alias examples for display"""
        examples = {}
        
        for product, aliases in product_aliases.items():
            if aliases:
                key = aliases[0].replace('.', '_').replace('#', 'sharp')
                examples[key] = f"{', '.join(aliases[:3])} → {product}"
        
        return examples
    
    def get_global_patterns(self) -> Dict[str, Dict]:
        """Get global patterns for AI hints"""
        return {
            'time_expressions': self.get_aliases_for_category('time_aliases'),
            'quantity_expressions': self.get_aliases_for_category('quantity_aliases'),
            'comparison_expressions': self.get_aliases_for_category('comparison_aliases')
        }


# Backward compatibility alias
ProductAliasMapper = UniversalAliasMapper
