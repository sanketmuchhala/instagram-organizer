"""Main desktop GUI for Instagram Link Organizer"""
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import webbrowser
from typing import List, Optional

from src.database.connection import db
from src.database.models import Category
from src.services.link_service import LinkService
from src.services.categorizer import SmartCategorizer


class InstagramOrganizerApp:
    """Main application window"""

    def __init__(self):
        # Initialize services
        if not db.connect():
            messagebox.showerror("Database Error", "Could not connect to MongoDB. Please check your .env file.")
            return

        self.link_service = LinkService()
        self.categorizer = SmartCategorizer()

        # Setup main window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Instagram Link Organizer")
        self.root.geometry("1200x800")

        # State
        self.current_filter_categories = []
        self.current_filter_tags = []
        self.selected_link_id = None

        # Build UI
        self._build_ui()

        # Load initial data
        self.refresh_links()
        self.update_statistics()

    def _build_ui(self):
        """Build the user interface"""
        # Main container
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="📸 Instagram Link Organizer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # Create tabs
        self.tabview = ctk.CTkTabview(main_container)
        self.tabview.pack(fill="both", expand=True)

        self.tab_add = self.tabview.add("Add Link")
        self.tab_browse = self.tabview.add("Browse Links")
        self.tab_stats = self.tabview.add("Statistics")

        # Build each tab
        self._build_add_tab()
        self._build_browse_tab()
        self._build_stats_tab()

    def _build_add_tab(self):
        """Build the Add Link tab"""
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.tab_add)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # URL
        ctk.CTkLabel(scroll_frame, text="Instagram URL:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.url_entry = ctk.CTkEntry(scroll_frame, placeholder_text="https://www.instagram.com/p/...")
        self.url_entry.pack(fill="x", pady=(0, 15))

        # Description
        ctk.CTkLabel(scroll_frame, text="Description:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        self.description_text = ctk.CTkTextbox(scroll_frame, height=100)
        self.description_text.pack(fill="x", pady=(0, 15))

        # Auto-categorize button
        analyze_btn = ctk.CTkButton(
            scroll_frame,
            text="🤖 Auto-Analyze Description",
            command=self.auto_analyze,
            fg_color="green",
            hover_color="darkgreen"
        )
        analyze_btn.pack(fill="x", pady=(0, 15))

        # Detected categories label
        self.detected_categories_label = ctk.CTkLabel(
            scroll_frame,
            text="Detected categories will appear here",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.detected_categories_label.pack(anchor="w", pady=(0, 15))

        # Manual categories selection
        ctk.CTkLabel(scroll_frame, text="Add/Remove Categories:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))

        # Main categories
        main_categories = Category.get_main_categories()
        self.category_vars = {}

        for cat in main_categories:
            var = ctk.BooleanVar(value=False)
            self.category_vars[cat] = var
            cb = ctk.CTkCheckBox(scroll_frame, text=cat.capitalize(), variable=var)
            cb.pack(anchor="w", padx=20, pady=2)

        # Notes
        ctk.CTkLabel(scroll_frame, text="Notes (optional):", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(15, 5))
        self.notes_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Additional notes...")
        self.notes_entry.pack(fill="x", pady=(0, 15))

        # Favorite checkbox
        self.favorite_var = ctk.BooleanVar(value=False)
        favorite_cb = ctk.CTkCheckBox(scroll_frame, text="⭐ Mark as Favorite", variable=self.favorite_var)
        favorite_cb.pack(anchor="w", pady=(0, 15))

        # Add button
        add_btn = ctk.CTkButton(
            scroll_frame,
            text="➕ Add Link",
            command=self.add_link,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        add_btn.pack(fill="x", pady=(10, 0))

    def _build_browse_tab(self):
        """Build the Browse Links tab"""
        # Top frame for filters
        filter_frame = ctk.CTkFrame(self.tab_browse)
        filter_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Search
        ctk.CTkLabel(filter_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search in description, notes, URL...")
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Filter by category
        ctk.CTkLabel(filter_frame, text="Category:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.filter_category_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Categories"] + Category.get_all_categories(),
            command=self.on_filter_change
        )
        self.filter_category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.filter_category_menu.set("All Categories")

        # Favorites only
        self.favorites_only_var = ctk.BooleanVar(value=False)
        favorites_cb = ctk.CTkCheckBox(
            filter_frame,
            text="⭐ Favorites Only",
            variable=self.favorites_only_var,
            command=self.on_filter_change
        )
        favorites_cb.grid(row=1, column=2, padx=5, pady=5)

        # Search button
        search_btn = ctk.CTkButton(filter_frame, text="🔍 Search", command=self.on_filter_change, width=100)
        search_btn.grid(row=0, column=2, padx=5, pady=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(filter_frame, text="🔄 Refresh", command=self.refresh_links, width=100)
        refresh_btn.grid(row=0, column=3, padx=5, pady=5)

        filter_frame.columnconfigure(1, weight=1)

        # Links display area
        self.links_frame = ctk.CTkScrollableFrame(self.tab_browse)
        self.links_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _build_stats_tab(self):
        """Build the Statistics tab"""
        scroll_frame = ctk.CTkScrollableFrame(self.tab_stats)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Stats display
        self.stats_label = ctk.CTkLabel(
            scroll_frame,
            text="Loading statistics...",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        self.stats_label.pack(anchor="w", pady=20)

    def auto_analyze(self):
        """Auto-analyze description and suggest categories"""
        description = self.description_text.get("1.0", "end-1c")
        url = self.url_entry.get()

        if not description.strip():
            messagebox.showwarning("No Description", "Please enter a description to analyze.")
            return

        # Get suggested categories
        categories = self.categorizer.analyze_description(description, url)

        if categories:
            # Update checkboxes
            for cat, var in self.category_vars.items():
                var.set(cat in categories)

            # Update label
            self.detected_categories_label.configure(
                text=f"✅ Detected: {', '.join(categories)}",
                text_color="green"
            )
        else:
            self.detected_categories_label.configure(
                text="❌ No categories detected. Try adding more details to the description.",
                text_color="orange"
            )

    def add_link(self):
        """Add a new link"""
        url = self.url_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        notes = self.notes_entry.get().strip()
        is_favorite = self.favorite_var.get()

        if not url:
            messagebox.showerror("Error", "Please enter an Instagram URL.")
            return

        # Get selected categories
        manual_categories = [cat for cat, var in self.category_vars.items() if var.get()]

        # Add link
        link = self.link_service.add_link(
            url=url,
            description=description,
            auto_categorize=True,
            manual_categories=manual_categories,
            notes=notes,
            is_favorite=is_favorite
        )

        if link:
            messagebox.showinfo("Success", f"Link added successfully!\n\nCategories: {', '.join(link.categories) if link.categories else 'None'}")

            # Clear form
            self.url_entry.delete(0, "end")
            self.description_text.delete("1.0", "end")
            self.notes_entry.delete(0, "end")
            self.favorite_var.set(False)
            for var in self.category_vars.values():
                var.set(False)
            self.detected_categories_label.configure(
                text="Detected categories will appear here",
                text_color="gray"
            )

            # Refresh browse tab
            self.refresh_links()
            self.update_statistics()
        else:
            messagebox.showerror("Error", "Failed to add link. It may already exist in the database.")

    def refresh_links(self):
        """Refresh the links display"""
        # Clear current display
        for widget in self.links_frame.winfo_children():
            widget.destroy()

        # Get filters
        query = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""
        category_filter = self.filter_category_menu.get() if hasattr(self, 'filter_category_menu') else "All Categories"
        favorites_only = self.favorites_only_var.get() if hasattr(self, 'favorites_only_var') else False

        # Build filter
        categories = None if category_filter == "All Categories" else [category_filter]

        # Get links
        links = self.link_service.search_links(
            query=query,
            categories=categories,
            is_favorite=favorites_only if favorites_only else None
        )

        if not links:
            no_links_label = ctk.CTkLabel(
                self.links_frame,
                text="No links found. Add some links to get started!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_links_label.pack(pady=50)
            return

        # Display links
        for link in links:
            self._create_link_card(link)

    def _create_link_card(self, link):
        """Create a card widget for a link"""
        # Card frame
        card = ctk.CTkFrame(self.links_frame, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)

        # Top row: favorite and delete
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(10, 0))

        # Favorite button
        fav_text = "⭐" if link.is_favorite else "☆"
        fav_btn = ctk.CTkButton(
            top_row,
            text=fav_text,
            width=40,
            command=lambda: self.toggle_favorite(str(link._id))
        )
        fav_btn.pack(side="left", padx=(0, 5))

        # Delete button
        del_btn = ctk.CTkButton(
            top_row,
            text="🗑️",
            width=40,
            fg_color="red",
            hover_color="darkred",
            command=lambda: self.delete_link(str(link._id))
        )
        del_btn.pack(side="right")

        # URL (clickable)
        url_btn = ctk.CTkButton(
            card,
            text=link.url,
            command=lambda: webbrowser.open(link.url),
            fg_color="transparent",
            hover_color="gray25",
            anchor="w"
        )
        url_btn.pack(fill="x", padx=10, pady=5)

        # Categories
        if link.categories:
            categories_text = "📁 " + ", ".join(link.categories)
            cat_label = ctk.CTkLabel(
                card,
                text=categories_text,
                font=ctk.CTkFont(size=12),
                text_color="lightblue",
                anchor="w"
            )
            cat_label.pack(fill="x", padx=10, pady=2)

        # Description
        if link.description:
            desc_preview = link.description[:200] + "..." if len(link.description) > 200 else link.description
            desc_label = ctk.CTkLabel(
                card,
                text=desc_preview,
                font=ctk.CTkFont(size=11),
                text_color="gray70",
                anchor="w",
                wraplength=1000
            )
            desc_label.pack(fill="x", padx=10, pady=2)

        # Notes
        if link.notes:
            notes_label = ctk.CTkLabel(
                card,
                text=f"📝 {link.notes}",
                font=ctk.CTkFont(size=11),
                text_color="yellow",
                anchor="w"
            )
            notes_label.pack(fill="x", padx=10, pady=2)

        # Date
        date_str = link.created_at.strftime("%Y-%m-%d %H:%M") if link.created_at else "Unknown"
        date_label = ctk.CTkLabel(
            card,
            text=f"Added: {date_str}",
            font=ctk.CTkFont(size=10),
            text_color="gray50",
            anchor="w"
        )
        date_label.pack(fill="x", padx=10, pady=(2, 10))

    def toggle_favorite(self, link_id: str):
        """Toggle favorite status"""
        if self.link_service.toggle_favorite(link_id):
            self.refresh_links()
            self.update_statistics()

    def delete_link(self, link_id: str):
        """Delete a link"""
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this link?")
        if result:
            if self.link_service.delete_link(link_id):
                messagebox.showinfo("Success", "Link deleted successfully.")
                self.refresh_links()
                self.update_statistics()
            else:
                messagebox.showerror("Error", "Failed to delete link.")

    def on_filter_change(self, *args):
        """Handle filter changes"""
        self.refresh_links()

    def update_statistics(self):
        """Update statistics display"""
        stats = self.link_service.get_statistics()

        stats_text = f"""
📊 STATISTICS

Total Links: {stats['total_links']}
⭐ Favorites: {stats['favorites']}
📅 Added This Week: {stats['recent_additions']}

🏆 TOP CATEGORIES:
"""

        for item in stats['top_categories']:
            stats_text += f"   • {item['category']}: {item['count']} links\n"

        self.stats_label.configure(text=stats_text)

    def run(self):
        """Start the application"""
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        db.close()
        self.root.destroy()


def main():
    """Main entry point"""
    app = InstagramOrganizerApp()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()


if __name__ == "__main__":
    main()
