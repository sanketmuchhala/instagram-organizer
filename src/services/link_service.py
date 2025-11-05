"""Service for managing Instagram links"""
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection

from src.database.connection import db
from src.database.models import InstagramLink
from src.services.categorizer import SmartCategorizer


class LinkService:
    """Service for CRUD operations on Instagram links"""

    def __init__(self):
        self.database = db.get_database()
        self.collection: Collection = self.database['instagram_links']
        self.categorizer = SmartCategorizer()

        # Create indexes for better query performance
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        try:
            self.collection.create_index('url', unique=True)
            self.collection.create_index('categories')
            self.collection.create_index('tags')
            self.collection.create_index('created_at')
            self.collection.create_index('is_favorite')
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")

    def add_link(
        self,
        url: str,
        description: str = "",
        auto_categorize: bool = True,
        manual_categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notes: str = "",
        is_favorite: bool = False
    ) -> Optional[InstagramLink]:
        """
        Add a new Instagram link

        Args:
            url: Instagram URL
            description: Video/post description
            auto_categorize: Whether to auto-categorize based on description
            manual_categories: Manually specified categories
            tags: Tags for the link
            notes: Additional notes
            is_favorite: Mark as favorite

        Returns:
            Created InstagramLink object or None if error
        """
        try:
            # Determine categories
            categories = []

            if auto_categorize and description:
                auto_categories = self.categorizer.analyze_description(description, url)
                categories.extend(auto_categories)

            if manual_categories:
                categories.extend(manual_categories)

            # Remove duplicates and refine
            categories = list(set(categories))
            categories = self.categorizer.refine_categories(categories)

            # Auto-extract tags if not provided
            if tags is None and description:
                tags = self.categorizer.suggest_tags(description)

            # Create link object
            link = InstagramLink(
                url=url,
                description=description,
                categories=categories,
                tags=tags or [],
                notes=notes,
                is_favorite=is_favorite
            )

            # Insert into database
            result = self.collection.insert_one(link.to_dict())
            link._id = result.inserted_id

            print(f"Added link: {url}")
            print(f"Auto-detected categories: {', '.join(categories) if categories else 'None'}")

            return link

        except Exception as e:
            print(f"Error adding link: {e}")
            return None

    def get_link(self, link_id: str) -> Optional[InstagramLink]:
        """Get a link by ID"""
        try:
            doc = self.collection.find_one({'_id': ObjectId(link_id)})
            if doc:
                return InstagramLink.from_dict(doc)
            return None
        except Exception as e:
            print(f"Error getting link: {e}")
            return None

    def get_all_links(self, limit: int = 100) -> List[InstagramLink]:
        """Get all links, sorted by most recent first"""
        try:
            docs = self.collection.find().sort('created_at', -1).limit(limit)
            return [InstagramLink.from_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Error getting links: {e}")
            return []

    def search_links(
        self,
        query: str = "",
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_favorite: Optional[bool] = None,
        limit: int = 100
    ) -> List[InstagramLink]:
        """
        Search links with filters

        Args:
            query: Text search in description and notes
            categories: Filter by categories (OR logic)
            tags: Filter by tags (OR logic)
            is_favorite: Filter by favorite status
            limit: Maximum results

        Returns:
            List of matching InstagramLink objects
        """
        try:
            filter_dict = {}

            # Text search
            if query:
                filter_dict['$or'] = [
                    {'description': {'$regex': query, '$options': 'i'}},
                    {'notes': {'$regex': query, '$options': 'i'}},
                    {'url': {'$regex': query, '$options': 'i'}}
                ]

            # Category filter
            if categories:
                filter_dict['categories'] = {'$in': categories}

            # Tag filter
            if tags:
                filter_dict['tags'] = {'$in': tags}

            # Favorite filter
            if is_favorite is not None:
                filter_dict['is_favorite'] = is_favorite

            docs = self.collection.find(filter_dict).sort('created_at', -1).limit(limit)
            return [InstagramLink.from_dict(doc) for doc in docs]

        except Exception as e:
            print(f"Error searching links: {e}")
            return []

    def update_link(
        self,
        link_id: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        auto_recategorize: bool = False
    ) -> bool:
        """
        Update a link

        Args:
            link_id: Link ID to update
            url: New URL
            description: New description
            categories: New categories
            tags: New tags
            notes: New notes
            is_favorite: New favorite status
            auto_recategorize: Re-run auto-categorization

        Returns:
            True if successful, False otherwise
        """
        try:
            update_dict = {}

            if url is not None:
                update_dict['url'] = url

            if description is not None:
                update_dict['description'] = description

                # Auto-recategorize if requested
                if auto_recategorize:
                    auto_categories = self.categorizer.analyze_description(description, url or "")
                    if categories:
                        categories = list(set(categories + auto_categories))
                    else:
                        categories = auto_categories

            if categories is not None:
                update_dict['categories'] = self.categorizer.refine_categories(categories)

            if tags is not None:
                update_dict['tags'] = tags

            if notes is not None:
                update_dict['notes'] = notes

            if is_favorite is not None:
                update_dict['is_favorite'] = is_favorite

            if not update_dict:
                return True  # Nothing to update

            result = self.collection.update_one(
                {'_id': ObjectId(link_id)},
                {'$set': update_dict}
            )

            return result.modified_count > 0

        except Exception as e:
            print(f"Error updating link: {e}")
            return False

    def delete_link(self, link_id: str) -> bool:
        """Delete a link"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(link_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting link: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get statistics about the link collection"""
        try:
            total_links = self.collection.count_documents({})
            favorites = self.collection.count_documents({'is_favorite': True})

            # Category distribution
            pipeline = [
                {'$unwind': '$categories'},
                {'$group': {'_id': '$categories', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]
            top_categories = list(self.collection.aggregate(pipeline))

            # Recent additions
            recent_date = datetime.utcnow()
            recent_date = recent_date.replace(day=recent_date.day - 7)  # Last 7 days
            recent_links = self.collection.count_documents({
                'created_at': {'$gte': recent_date}
            })

            return {
                'total_links': total_links,
                'favorites': favorites,
                'recent_additions': recent_links,
                'top_categories': [
                    {'category': item['_id'], 'count': item['count']}
                    for item in top_categories
                ]
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_links': 0,
                'favorites': 0,
                'recent_additions': 0,
                'top_categories': []
            }

    def get_all_used_categories(self) -> List[str]:
        """Get all categories that are currently in use"""
        try:
            categories = self.collection.distinct('categories')
            return sorted(categories)
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def get_all_used_tags(self) -> List[str]:
        """Get all tags that are currently in use"""
        try:
            tags = self.collection.distinct('tags')
            return sorted(tags)
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []

    def toggle_favorite(self, link_id: str) -> bool:
        """Toggle favorite status of a link"""
        try:
            link = self.get_link(link_id)
            if link:
                return self.update_link(link_id, is_favorite=not link.is_favorite)
            return False
        except Exception as e:
            print(f"Error toggling favorite: {e}")
            return False
