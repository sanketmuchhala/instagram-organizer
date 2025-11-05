# 📸 Instagram Link Organizer

A smart desktop application to organize your Instagram links with automatic categorization powered by AI.

## ✨ Features

- **🤖 Smart Auto-Categorization**: Automatically categorizes links based on video descriptions
- **📁 Hierarchical Categories**: Organize by recipes (cuisine, diet type, meal type), fitness, fashion, travel, and more
- **🔍 Advanced Search**: Filter by categories, tags, favorites, or search text
- **⭐ Favorites**: Mark important links as favorites for quick access
- **📊 Statistics**: Track your collection with detailed statistics
- **🎨 Modern UI**: Beautiful dark-themed desktop interface built with CustomTkinter

## 🎯 Smart Categorization Examples

The app intelligently categorizes your Instagram links based on their descriptions:

### Recipe Examples
- **"Delicious butter chicken recipe with homemade naan"**
  - Categories: `recipes`, `indian`, `non-vegetarian`, `dinner`

- **"Quick 15-minute vegan pasta for busy weeknights"**
  - Categories: `recipes`, `italian`, `vegan`, `quick-meal`, `dinner`

- **"Healthy breakfast smoothie bowl with superfoods"**
  - Categories: `recipes`, `healthy`, `breakfast`, `vegetarian`

- **"Loaded cheesy pizza - the ultimate cheat meal!"**
  - Categories: `recipes`, `italian`, `cheat-meal`, `non-vegetarian`

### Other Category Examples
- **Fitness**: Workout videos, yoga poses, exercise routines
- **Fashion**: Outfit ideas, styling tips, makeup tutorials
- **Travel**: Destination guides, travel tips, food adventures
- **Lifestyle**: Home decor, productivity tips, organization hacks

## 🚀 Installation

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **MongoDB Atlas Account** (Free tier available)
   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - Get your connection string

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB connection**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your MongoDB connection string:
   ```
   MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=instagram_organizer
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📖 How to Use

### Adding a Link

1. Go to the **"Add Link"** tab
2. Paste your Instagram URL
3. Add the video/post description
4. Click **"🤖 Auto-Analyze Description"** to automatically detect categories
5. Manually adjust categories if needed
6. Add optional notes
7. Mark as favorite (optional)
8. Click **"➕ Add Link"**

### Browsing Links

1. Go to the **"Browse Links"** tab
2. Use the search bar to find specific content
3. Filter by category using the dropdown
4. Toggle "⭐ Favorites Only" to see only favorite links
5. Click any URL to open it in your browser
6. Toggle favorite status with the ⭐ button
7. Delete links with the 🗑️ button

### Viewing Statistics

1. Go to the **"Statistics"** tab
2. See total links, favorites, recent additions
3. View top categories by usage

## 🗂️ Category Structure

The app organizes links using a hierarchical category system:

### Main Categories

- **Recipes**
  - Cuisine: Indian, Italian, Mexican, Chinese, Thai, American, Mediterranean
  - Diet: Vegetarian, Vegan, Non-Vegetarian, Gluten-Free, Keto, Paleo
  - Type: Healthy, Cheat Meal, Quick Meal, Meal Prep
  - Meal: Breakfast, Lunch, Dinner, Snack, Dessert, Beverage

- **Fitness**
  - Type: Workout, Yoga, Cardio, Strength, HIIT
  - Level: Beginner, Intermediate, Advanced

- **Fashion**
  - Type: Outfit, Styling Tips, Accessories, Makeup, Hairstyle
  - Season: Summer, Winter, Fall, Spring

- **Travel**
  - Type: Destination, Tips, Food, Culture, Adventure
  - Region: Asia, Europe, Africa, Americas, Oceania

- **Lifestyle**
  - Type: Home Decor, Productivity, Motivation, Self-Care

- **Education**
  - Type: Tutorial, Tips, How-To, Review

- **Entertainment**
  - Type: Funny, Meme, Music, Dance, Art, Photography

## 🛠️ Technical Details

### Technology Stack

- **Python 3.8+**
- **CustomTkinter**: Modern GUI framework
- **MongoDB**: Cloud database (MongoDB Atlas)
- **PyMongo**: MongoDB driver
- **python-dotenv**: Environment configuration

### Project Structure

```
instagram-organizer/
├── src/
│   ├── database/
│   │   ├── connection.py      # MongoDB connection
│   │   └── models.py          # Data models
│   ├── services/
│   │   ├── categorizer.py     # Smart categorization engine
│   │   └── link_service.py    # Business logic
│   └── gui/
│       └── main_window.py     # Desktop UI
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

### Smart Categorization Algorithm

The categorization service uses keyword matching with the following approach:

1. **Text Preprocessing**: Converts description to lowercase, removes special characters
2. **Keyword Matching**: Matches against 500+ predefined keywords for each category
3. **Pattern Recognition**: Uses word boundary matching for accurate detection
4. **Hierarchy Refinement**: Ensures parent categories are included when subcategories are detected
5. **Confidence Scoring**: Calculates confidence levels for category suggestions

## 🔒 Privacy & Security

- All data is stored in your personal MongoDB database
- No data is shared with third parties
- Connection strings are stored securely in `.env` file (not tracked by git)
- Instagram links are stored as-is without fetching content

## 🐛 Troubleshooting

### "Could not connect to MongoDB"
- Check your `.env` file has the correct `MONGODB_URI`
- Verify your MongoDB Atlas cluster is running
- Ensure your IP address is whitelisted in MongoDB Atlas Network Access

### "ModuleNotFoundError"
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try creating a virtual environment first

### GUI doesn't appear
- Ensure you have tkinter installed (usually comes with Python)
- On Linux, you may need: `sudo apt-get install python3-tk`

## 🚀 Future Enhancements

- [ ] Import Instagram links directly from browser history
- [ ] Bulk import from CSV/JSON
- [ ] Advanced filtering with multiple category combinations
- [ ] Export links to various formats
- [ ] Desktop notifications for new additions
- [ ] Mobile companion app
- [ ] Collaborative collections (share with friends)

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Happy Organizing! 📸✨**
