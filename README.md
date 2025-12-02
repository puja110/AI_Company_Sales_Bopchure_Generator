# 🎨 AI Brochure Generator

Transform any company website into a professional brochure using AI.

## Features

- 🔍 Intelligent link detection and content extraction
- 🤖 AI-powered brochure generation using OpenAI GPT models
- ⚡ Real-time streaming for live content generation
- 💾 Multiple export formats (Markdown, HTML)
- 🎨 Beautiful, responsive web interface
- 📱 Mobile-friendly design

## Technologies Used

- **Backend:** Flask (Python)
- **AI:** OpenAI GPT-4
- **Web Scraping:** BeautifulSoup4
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Custom CSS with gradient animations

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API Key

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/brochure-generator.git
cd brochure-generator
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file:

```env
OPENAI_API_KEY=your-api-key-here
```

5. Run the application:

```bash
python app.py
```

6. Open browser and go to: `http://localhost:5000`

## Usage

1. Enter the company name
2. Enter the company website URL
3. Choose streaming mode (optional)
4. Click "Generate Brochure"
5. Download in your preferred format

## Command Line Interface

You can also use the CLI:

```bash
python main.py "Company Name" "https://company.com" --stream
```

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `PORT` - Port to run the server (default: 5000)
- `FLASK_ENV` - Set to 'production' for production mode

## Project Structure

```
brochure-generator/
├── app.py                    # Flask web server
├── brochure_generator.py     # Core brochure generation logic
├── scraper.py                # Web scraping utilities
├── main.py                   # Command-line interface
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface
└── static/
    ├── css/
    │   └── style.css        # Styling
    └── js/
        └── script.js        # Frontend logic
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Your Name - [Your GitHub](https://github.com/yourusername)

## Acknowledgments

- OpenAI for providing the GPT API
- Flask framework
- BeautifulSoup4 for web scraping
