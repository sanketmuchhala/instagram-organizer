"""Smart categorization service for Instagram links"""
import re
from typing import List, Set
from src.database.models import Category


class SmartCategorizer:
    """Automatically categorize Instagram links based on description"""

    # Keyword mappings for categories
    KEYWORD_MAP = {
        # Main categories
        'recipes': [
            'recipe', 'cooking', 'cook', 'food', 'dish', 'meal', 'ingredient',
            'kitchen', 'bake', 'baking', 'chef', 'cuisine', 'delicious', 'tasty',
            'yummy', 'eat', 'eating', 'make', 'prepare', 'homemade'
        ],
        'fitness': [
            'workout', 'exercise', 'fitness', 'gym', 'training', 'health',
            'muscle', 'cardio', 'yoga', 'pilates', 'strength', 'run', 'running',
            'weight', 'lose weight', 'gain', 'fit', 'active', 'athletic'
        ],
        'fashion': [
            'fashion', 'style', 'outfit', 'wear', 'clothing', 'dress', 'look',
            'trend', 'trendy', 'accessory', 'shoes', 'makeup', 'beauty', 'hair',
            'wardrobe', 'ootd', 'fashionable', 'chic', 'elegant'
        ],
        'travel': [
            'travel', 'trip', 'journey', 'vacation', 'destination', 'explore',
            'adventure', 'tour', 'visit', 'visiting', 'tourist', 'wanderlust',
            'backpack', 'flight', 'hotel', 'beach', 'mountain', 'city', 'country'
        ],
        'lifestyle': [
            'lifestyle', 'home', 'decor', 'interior', 'organize', 'organization',
            'productivity', 'motivation', 'routine', 'daily', 'self-care', 'wellness',
            'mindfulness', 'living', 'life', 'apartment', 'house'
        ],
        'education': [
            'learn', 'tutorial', 'how to', 'guide', 'tips', 'trick', 'hack',
            'teach', 'education', 'lesson', 'course', 'study', 'knowledge',
            'information', 'fact', 'review', 'explain', 'demonstration'
        ],
        'entertainment': [
            'funny', 'fun', 'lol', 'hilarious', 'comedy', 'laugh', 'meme',
            'music', 'dance', 'dancing', 'art', 'artist', 'creative', 'photo',
            'photography', 'video', 'entertainment', 'enjoy'
        ],

        # Cuisine subcategories
        'indian': [
            'indian', 'india', 'curry', 'masala', 'biryani', 'tandoor', 'naan',
            'roti', 'daal', 'dal', 'paneer', 'samosa', 'dosa', 'idli', 'chaat',
            'tikka', 'butter chicken', 'vindaloo', 'korma', 'punjabi', 'south indian'
        ],
        'italian': [
            'italian', 'italy', 'pasta', 'pizza', 'spaghetti', 'lasagna',
            'risotto', 'pesto', 'carbonara', 'marinara', 'bolognese', 'ravioli',
            'gnocchi', 'tiramisu', 'bruschetta', 'mozzarella', 'parmesan'
        ],
        'mexican': [
            'mexican', 'mexico', 'taco', 'burrito', 'quesadilla', 'enchilada',
            'guacamole', 'salsa', 'tortilla', 'nachos', 'fajita', 'chimichanga',
            'tamale', 'chile', 'jalapeno'
        ],
        'chinese': [
            'chinese', 'china', 'stir fry', 'wok', 'dumpling', 'dim sum',
            'fried rice', 'noodles', 'chow mein', 'kung pao', 'sweet and sour',
            'szechuan', 'cantonese', 'spring roll', 'baozi', 'congee'
        ],
        'thai': [
            'thai', 'thailand', 'pad thai', 'curry', 'coconut', 'lemongrass',
            'basil', 'tom yum', 'green curry', 'red curry', 'massaman', 'papaya salad'
        ],
        'american': [
            'american', 'burger', 'bbq', 'barbecue', 'steak', 'fries', 'hot dog',
            'sandwich', 'mac and cheese', 'fried chicken', 'ribs', 'southern',
            'cajun', 'texan', 'soul food'
        ],
        'mediterranean': [
            'mediterranean', 'greek', 'falafel', 'hummus', 'pita', 'shawarma',
            'kebab', 'tabouleh', 'tzatziki', 'olive', 'feta', 'couscous'
        ],

        # Diet subcategories
        'vegetarian': [
            'vegetarian', 'veggie', 'veg', 'vegetables', 'plant-based',
            'meatless', 'no meat', 'meat-free'
        ],
        'vegan': [
            'vegan', 'plant-based', 'dairy-free', 'no dairy', 'no animal',
            'cruelty-free'
        ],
        'non-vegetarian': [
            'non-veg', 'non vegetarian', 'meat', 'chicken', 'beef', 'pork',
            'lamb', 'mutton', 'fish', 'seafood', 'shrimp', 'salmon', 'turkey'
        ],
        'gluten-free': [
            'gluten-free', 'gluten free', 'no gluten', 'celiac', 'gf'
        ],
        'keto': [
            'keto', 'ketogenic', 'low carb', 'low-carb', 'high fat', 'lchf'
        ],
        'paleo': [
            'paleo', 'paleolithic', 'primal', 'caveman diet', 'whole30'
        ],

        # Type subcategories
        'healthy': [
            'healthy', 'health', 'nutritious', 'nutrition', 'clean eating',
            'wholesome', 'balanced', 'superfood', 'detox', 'low calorie',
            'low-fat', 'diet', 'fitness food', 'protein', 'vitamins'
        ],
        'cheat-meal': [
            'cheat meal', 'cheat day', 'indulge', 'indulgent', 'guilty pleasure',
            'treat', 'decadent', 'rich', 'comfort food', 'loaded', 'fried',
            'crispy', 'creamy', 'cheesy'
        ],
        'quick-meal': [
            'quick', 'fast', 'easy', 'simple', '5 minute', '10 minute',
            '15 minute', '20 minute', 'instant', 'rapid', 'speedy', 'one pot'
        ],
        'meal-prep': [
            'meal prep', 'batch cooking', 'make ahead', 'prep', 'weekly',
            'food prep', 'prepare in advance', 'freezer meal'
        ],

        # Meal subcategories
        'breakfast': [
            'breakfast', 'brunch', 'morning', 'pancake', 'waffle', 'omelette',
            'cereal', 'oats', 'smoothie bowl', 'toast', 'bagel', 'muffin'
        ],
        'lunch': [
            'lunch', 'midday', 'noon', 'lunch box', 'sandwich', 'wrap', 'salad'
        ],
        'dinner': [
            'dinner', 'supper', 'evening meal', 'main course', 'entree'
        ],
        'snack': [
            'snack', 'appetizer', 'starter', 'finger food', 'bite', 'munchies',
            'nibbles', 'side'
        ],
        'dessert': [
            'dessert', 'sweet', 'cake', 'cookie', 'brownie', 'ice cream',
            'pudding', 'pie', 'pastry', 'chocolate', 'candy', 'treat'
        ],
        'beverage': [
            'drink', 'beverage', 'juice', 'smoothie', 'shake', 'coffee',
            'tea', 'cocktail', 'mocktail', 'latte', 'refreshing', 'sip'
        ],

        # Fitness subcategories
        'workout': [
            'workout', 'exercise routine', 'training session', 'sweat',
            'circuit', 'reps', 'sets', 'gym session'
        ],
        'yoga': [
            'yoga', 'asana', 'namaste', 'meditation', 'zen', 'flow',
            'vinyasa', 'hatha', 'ashtanga', 'pose', 'stretch'
        ],
        'cardio': [
            'cardio', 'aerobic', 'running', 'jogging', 'cycling', 'hiit',
            'jumping', 'burpee', 'endurance', 'heart rate'
        ],
        'strength': [
            'strength', 'weights', 'lifting', 'dumbbells', 'barbell',
            'resistance', 'muscle building', 'bodybuilding', 'powerlifting'
        ],

        # Fitness level
        'beginner': [
            'beginner', 'beginners', 'start', 'starting', 'newbie', 'basic',
            'easy', 'simple', 'introduction', 'intro', 'first time'
        ],
        'intermediate': [
            'intermediate', 'moderate', 'medium', 'next level', 'progress'
        ],
        'advanced': [
            'advanced', 'expert', 'pro', 'professional', 'master', 'extreme',
            'challenging', 'difficult', 'hard'
        ]
    }

    def __init__(self):
        self.category_tree = Category.CATEGORY_TREE

    def analyze_description(self, description: str, url: str = "") -> List[str]:
        """
        Analyze description and return suggested categories

        Args:
            description: Video/post description text
            url: Instagram URL (optional, for context)

        Returns:
            List of suggested category names
        """
        if not description:
            return []

        # Convert to lowercase for matching
        text = (description + " " + url).lower()

        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text)

        # Find matching categories
        matched_categories: Set[str] = set()

        for category, keywords in self.KEYWORD_MAP.items():
            for keyword in keywords:
                # Use word boundary matching for better accuracy
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    matched_categories.add(category)
                    break  # Found one keyword for this category, move to next category

        return sorted(list(matched_categories))

    def suggest_tags(self, description: str) -> List[str]:
        """
        Extract potential tags from description

        Args:
            description: Video/post description text

        Returns:
            List of suggested tags
        """
        if not description:
            return []

        tags = []

        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', description)
        tags.extend([tag.lower() for tag in hashtags])

        # Extract @mentions (could be collaborators or brands)
        mentions = re.findall(r'@(\w+)', description)
        tags.extend([f"@{mention.lower()}" for mention in mentions])

        return list(set(tags))[:10]  # Limit to 10 unique tags

    def get_category_confidence(self, description: str, category: str) -> float:
        """
        Calculate confidence score for a category match

        Args:
            description: Video/post description text
            category: Category name to check

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not description or category not in self.KEYWORD_MAP:
            return 0.0

        text = description.lower()
        keywords = self.KEYWORD_MAP[category]

        matches = 0
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                matches += 1

        # Confidence based on percentage of keywords matched
        confidence = min(matches / max(len(keywords) * 0.1, 1), 1.0)
        return confidence

    def refine_categories(self, categories: List[str]) -> List[str]:
        """
        Refine category list to ensure logical consistency

        Args:
            categories: Initial category list

        Returns:
            Refined category list
        """
        refined = set(categories)

        # Ensure main category is included if subcategories are present
        main_categories = Category.get_main_categories()

        for main_cat in main_categories:
            subcats = Category.get_subcategories(main_cat)
            if subcats:
                # Get all possible subcategory values
                all_subcat_values = []
                for subcat_list in subcats.values():
                    if isinstance(subcat_list, list):
                        all_subcat_values.extend(subcat_list)

                # If any subcategory is in our categories, add main category
                if any(subcat in categories for subcat in all_subcat_values):
                    refined.add(main_cat)

        return sorted(list(refined))
