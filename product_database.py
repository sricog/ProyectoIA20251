#!/usr/bin/env python3
"""
Product Database Module - Production Ready Search System
Loads and manages product data from CSV with intelligent search capabilities
"""

import pandas as pd
import logging
from typing import List, Dict, Optional, Tuple
import re
from fuzzywuzzy import fuzz, process
from collections import defaultdict

logger = logging.getLogger(__name__)

class ProductDatabase:
    def __init__(self, csv_file: str = "data/product_data.csv"):
        """Initialize product database from CSV file"""
        self.df = None
        self.categories = set()
        self.brands = set()
        self.search_index = {}
        self.load_data(csv_file)

    def load_data(self, csv_file: str):
        """Load product data from CSV file"""
        try:
            self.df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(self.df)} products from {csv_file}")

            # Clean and prepare data
            self.df['precio'] = pd.to_numeric(self.df['precio'], errors='coerce')
            self.df['precio_de_descuento'] = pd.to_numeric(self.df['precio_de_descuento'], errors='coerce')

            # Extract unique categories and brands
            self.categories = set(self.df['categoria'].unique())
            self.brands = set(self.df['marca'].unique())

            # Create comprehensive search index
            self.df['search_text'] = (
                self.df['nombre_de_producto'].str.lower() + ' ' +
                self.df['categoria'].str.lower() + ' ' +
                self.df['marca'].str.lower()
            ).fillna('')

            # Build search index for fuzzy matching
            self._build_search_index()

            logger.info(f"Categories: {len(self.categories)}, Brands: {len(self.brands)}")
            logger.info(f"Products on sale: {len(self.df[self.df['en_descuento'] == True])}")
            logger.info(f"Average price: ${self.df['precio'].mean():.2f}")

        except Exception as e:
            logger.error(f"Error loading product data: {e}")
            raise

    def _build_search_index(self):
        """Build search index for fuzzy matching"""
        self.search_index = {
            'product_names': list(self.df['nombre_de_producto'].str.lower()),
            'brands': list(self.df['marca'].str.lower()),
            'categories': list(self.df['categoria'].str.lower()),
            'full_text': list(self.df['search_text'])
        }

    def intelligent_search(self, query: str, max_results: int = 8) -> Tuple[List[Dict], str]:
        """
        Intelligent search using multiple strategies without hardcoded patterns
        """
        if not query or not query.strip():
            return self.get_featured_products(max_results), "Productos destacados"

        query = query.strip().lower()
        results = []
        search_description = ""

        # Strategy 1: Exact text matching (highest priority)
        exact_results = self._exact_search(query, max_results)
        if exact_results:
            return exact_results, f"Resultados exactos para: '{query}'"

        # Strategy 2: Fuzzy product name matching
        fuzzy_results = self._fuzzy_product_search(query, max_results)
        if fuzzy_results:
            results.extend(fuzzy_results)
            search_description = f"Productos similares a: '{query}'"

        # Strategy 3: Brand fuzzy matching
        if not results:
            brand_results = self._fuzzy_brand_search(query, max_results)
            if brand_results:
                results.extend(brand_results)
                search_description = f"Productos de marca similar a: '{query}'"

        # Strategy 4: Category fuzzy matching
        if not results:
            category_results = self._fuzzy_category_search(query, max_results)
            if category_results:
                results.extend(category_results)
                search_description = f"Productos en categoría similar a: '{query}'"

        # Strategy 5: Full text search with ranking
        if not results:
            text_results = self._ranked_text_search(query, max_results)
            if text_results:
                results.extend(text_results)
                search_description = f"Resultados de búsqueda para: '{query}'"

        # Strategy 6: Smart alternatives (without hardcoding)
        if not results:
            alternative_results = self._find_smart_alternatives(query, max_results)
            if alternative_results:
                results.extend(alternative_results)
                search_description = f"Alternativas sugeridas para: '{query}'"

        # Fallback: Popular products
        if not results:
            results = self.get_featured_products(max_results)
            search_description = f"No se encontraron resultados para '{query}'. Productos populares:"

        # Remove duplicates and rank by relevance
        unique_results = self._remove_duplicates_and_rank(results, query)
        return unique_results[:max_results], search_description

    def _exact_search(self, query: str, max_results: int) -> List[Dict]:
        """Exact text matching in product names, brands, categories"""
        mask = (
            self.df['nombre_de_producto'].str.lower().str.contains(query, na=False) |
            self.df['marca'].str.lower().str.contains(query, na=False) |
            self.df['categoria'].str.lower().str.contains(query, na=False)
        )
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def _fuzzy_product_search(self, query: str, max_results: int) -> List[Dict]:
        """Fuzzy matching on product names"""
        if not self.search_index['product_names']:
            return []

        # Find best matches using fuzzy matching
        matches = process.extract(query, self.search_index['product_names'],
                                limit=max_results, scorer=fuzz.partial_ratio)

        # Filter matches with decent score (>60)
        good_matches = [match for match in matches if match[1] > 60]

        if not good_matches:
            return []

        # Get products for the best matches
        matched_names = [match[0] for match in good_matches]
        mask = self.df['nombre_de_producto'].str.lower().isin(matched_names)
        results = self.df[mask]
        return self._format_products(results)

    def _fuzzy_brand_search(self, query: str, max_results: int) -> List[Dict]:
        """Fuzzy matching on brand names"""
        unique_brands = list(self.brands)
        matches = process.extract(query, unique_brands, limit=3, scorer=fuzz.partial_ratio)
        good_matches = [match for match in matches if match[1] > 70]

        if not good_matches:
            return []

        matched_brands = [match[0] for match in good_matches]
        mask = self.df['marca'].isin(matched_brands)
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def _fuzzy_category_search(self, query: str, max_results: int) -> List[Dict]:
        """Fuzzy matching on categories"""
        unique_categories = list(self.categories)
        matches = process.extract(query, unique_categories, limit=2, scorer=fuzz.partial_ratio)
        good_matches = [match for match in matches if match[1] > 70]

        if not good_matches:
            return []

        matched_categories = [match[0] for match in good_matches]
        mask = self.df['categoria'].isin(matched_categories)
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def _ranked_text_search(self, query: str, max_results: int) -> List[Dict]:
        """Full text search with ranking"""
        query_words = query.split()
        scores = []

        for idx, text in enumerate(self.search_index['full_text']):
            score = 0
            for word in query_words:
                if word in text:
                    score += len(word)  # Longer words get higher scores
                # Add partial matching score
                score += fuzz.partial_ratio(word, text) / 100
            scores.append((idx, score))

        # Sort by score and get top results
        scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, score in scores[:max_results] if score > 0.5]

        if not top_indices:
            return []

        results = self.df.iloc[top_indices]
        return self._format_products(results)

    def _find_smart_alternatives(self, query: str, max_results: int) -> List[Dict]:
        """
        Find smart alternatives without hardcoding
        Uses semantic similarity and product relationships
        """
        # Extract key terms from query
        query_words = re.findall(r'\b\w+\b', query.lower())

        # Look for products that share key terms
        alternatives = []
        for word in query_words:
            if len(word) > 2:  # Skip short words
                word_results = self._exact_search(word, max_results // 2)
                alternatives.extend(word_results)

        return alternatives

    def _remove_duplicates_and_rank(self, products: List[Dict], query: str) -> List[Dict]:
        """Remove duplicates and rank by relevance to query"""
        seen_names = set()
        unique_products = []

        for product in products:
            if product['name'] not in seen_names:
                seen_names.add(product['name'])
                # Calculate relevance score
                relevance_score = self._calculate_relevance(product, query)
                product['_relevance_score'] = relevance_score
                unique_products.append(product)

        # Sort by relevance score (descending)
        unique_products.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)

        # Remove the temporary score field
        for product in unique_products:
            product.pop('_relevance_score', None)

        return unique_products

    def _calculate_relevance(self, product: Dict, query: str) -> float:
        """Calculate relevance score for ranking"""
        score = 0.0
        query_lower = query.lower()

        # Exact name match gets highest score
        if query_lower in product['name'].lower():
            score += 10.0

        # Brand match
        if query_lower in product['brand'].lower():
            score += 5.0

        # Category match
        if query_lower in product['category'].lower():
            score += 3.0

        # Fuzzy similarity score
        name_similarity = fuzz.partial_ratio(query_lower, product['name'].lower()) / 100
        score += name_similarity * 2

        # Boost products on sale
        if product['on_sale']:
            score += 1.0

        # Boost products with good availability
        if product['units_available'] > 10:
            score += 0.5

        return score

    def get_products_by_category(self, category: str, max_results: int = 10) -> List[Dict]:
        """Get products by category with fuzzy matching"""
        matches = process.extract(category, list(self.categories), limit=1, scorer=fuzz.partial_ratio)
        if not matches or matches[0][1] < 60:
            return []

        best_category = matches[0][0]
        mask = self.df['categoria'] == best_category
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def get_products_by_brand(self, brand: str, max_results: int = 10) -> List[Dict]:
        """Get products by brand with fuzzy matching"""
        matches = process.extract(brand, list(self.brands), limit=1, scorer=fuzz.partial_ratio)
        if not matches or matches[0][1] < 60:
            return []

        best_brand = matches[0][0]
        mask = self.df['marca'] == best_brand
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def get_products_on_sale(self, max_results: int = 10) -> List[Dict]:
        """Get products currently on sale"""
        if self.df is None:
            return []

        mask = self.df['en_descuento'] == True
        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def get_products_by_price_range(self, min_price: float = None, max_price: float = None, max_results: int = 10) -> List[Dict]:
        """Get products within price range"""
        if self.df is None:
            return []

        mask = pd.Series([True] * len(self.df))

        if min_price is not None:
            mask &= self.df['precio'] >= min_price

        if max_price is not None:
            mask &= self.df['precio'] <= max_price

        results = self.df[mask].head(max_results)
        return self._format_products(results)

    def get_featured_products(self, max_results: int = 10) -> List[Dict]:
        """Get featured products (mix of popular brands and good prices)"""
        if self.df is None:
            return []

        # Prioritize Apple, Samsung, Sony, Nike, Adidas products
        premium_brands = ['Apple', 'Samsung', 'Sony', 'Nike', 'Adidas', 'Gucci', 'Prada']

        # Get some premium brand products
        premium_mask = self.df['marca'].isin(premium_brands)
        premium_products = self.df[premium_mask].head(max_results // 2)

        # Get some products on sale
        sale_mask = self.df['en_descuento'] == True
        sale_products = self.df[sale_mask].head(max_results // 2)

        # Combine and remove duplicates
        featured = pd.concat([premium_products, sale_products]).drop_duplicates().head(max_results)

        return self._format_products(featured)

    def _format_products(self, df_subset: pd.DataFrame) -> List[Dict]:
        """Format DataFrame subset into product dictionaries"""
        products = []

        for _, row in df_subset.iterrows():
            # Calculate final price (with discount if applicable)
            final_price = row['precio']
            if row['en_descuento'] and pd.notna(row['precio_de_descuento']):
                final_price = row['precio_de_descuento']

            # Create description
            description = f"{row['marca']} - {row['categoria']}"
            if row['en_descuento']:
                discount_pct = int(((row['precio'] - final_price) / row['precio']) * 100) if final_price < row['precio'] else 0
                description += f" - ¡{discount_pct}% de descuento!"

            product = {
                'name': row['nombre_de_producto'],
                'brand': row['marca'],
                'category': row['categoria'],
                'price': final_price,
                'original_price': row['precio'] if row['en_descuento'] else None,
                'on_sale': bool(row['en_descuento']),
                'units_available': int(row['unidades_disponibles']),
                'description': description,
                'shipping': row['metodo_de_envio'],
                'payment_methods': row['metodos_de_pago'],
                'financing': row['opciones_de_financiacion'],
                'return_policy': row['politicas_de_devolucion']
            }
            products.append(product)

        return products

    # Backward compatibility - alias for intelligent_search
    def smart_search(self, user_query: str, max_results: int = 8) -> Tuple[List[Dict], str]:
        """Alias for intelligent_search for backward compatibility"""
        return self.intelligent_search(user_query, max_results)

# Global instance
product_db = ProductDatabase()

def get_product_database() -> ProductDatabase:
    """Get the global product database instance"""
    return product_db