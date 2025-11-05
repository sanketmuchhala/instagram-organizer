"""Data models for Instagram links"""
from datetime import datetime
from typing import List, Optional, Dict
from bson import ObjectId


class InstagramLink:
    """Model for Instagram link with categories"""

    def __init__(
        self,
        url: str,
        description: str = "",
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notes: str = "",
        is_favorite: bool = False,
        created_at: Optional[datetime] = None,
        _id: Optional[ObjectId] = None
    ):
        self.url = url
        self.description = description
        self.categories = categories or []
        self.tags = tags or []
        self.notes = notes
        self.is_favorite = is_favorite
        self.created_at = created_at or datetime.utcnow()
        self._id = _id

    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        doc = {
            'url': self.url,
            'description': self.description,
            'categories': self.categories,
            'tags': self.tags,
            'notes': self.notes,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at
        }
        if self._id:
            doc['_id'] = self._id
        return doc

    @classmethod
    def from_dict(cls, doc: Dict) -> 'InstagramLink':
        """Create instance from MongoDB document"""
        return cls(
            url=doc.get('url', ''),
            description=doc.get('description', ''),
            categories=doc.get('categories', []),
            tags=doc.get('tags', []),
            notes=doc.get('notes', ''),
            is_favorite=doc.get('is_favorite', False),
            created_at=doc.get('created_at'),
            _id=doc.get('_id')
        )

    def __str__(self):
        categories_str = ', '.join(self.categories) if self.categories else 'None'
        return f"Link: {self.url}\nCategories: {categories_str}\nDescription: {self.description[:50]}..."


class Category:
    """Model for category hierarchy"""

    # Predefined category structure
    CATEGORY_TREE = {
        'recipes': {
            'cuisine': ['indian', 'italian', 'mexican', 'chinese', 'thai', 'american', 'mediterranean', 'other'],
            'diet': ['vegetarian', 'vegan', 'non-vegetarian', 'pescatarian', 'gluten-free', 'keto', 'paleo'],
            'type': ['healthy', 'cheat-meal', 'comfort-food', 'quick-meal', 'meal-prep'],
            'meal': ['breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'beverage']
        },
        'fitness': {
            'type': ['workout', 'yoga', 'cardio', 'strength', 'flexibility', 'hiit'],
            'level': ['beginner', 'intermediate', 'advanced']
        },
        'fashion': {
            'type': ['outfit', 'styling-tips', 'accessories', 'shoes', 'makeup', 'hairstyle'],
            'season': ['summer', 'winter', 'fall', 'spring', 'all-season']
        },
        'travel': {
            'type': ['destination', 'tips', 'food', 'culture', 'adventure', 'budget-travel'],
            'region': ['asia', 'europe', 'africa', 'americas', 'oceania']
        },
        'lifestyle': {
            'type': ['home-decor', 'productivity', 'motivation', 'self-care', 'organization']
        },
        'education': {
            'type': ['tutorial', 'tips', 'facts', 'how-to', 'review']
        },
        'entertainment': {
            'type': ['funny', 'meme', 'music', 'dance', 'art', 'photography']
        }
    }

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get flat list of all categories"""
        categories = []
        for main_cat, subcats in cls.CATEGORY_TREE.items():
            categories.append(main_cat)
            if isinstance(subcats, dict):
                for subcat_list in subcats.values():
                    if isinstance(subcat_list, list):
                        categories.extend(subcat_list)
        return sorted(set(categories))

    @classmethod
    def get_main_categories(cls) -> List[str]:
        """Get main category names"""
        return list(cls.CATEGORY_TREE.keys())

    @classmethod
    def get_subcategories(cls, main_category: str) -> Dict[str, List[str]]:
        """Get subcategories for a main category"""
        return cls.CATEGORY_TREE.get(main_category, {})
