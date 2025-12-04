# 🎨 AI Brochure Generator

Transform any company website into a professional, interactive brochure using AI.

## ✨ Features

### Core Features

- 🤖 **AI-Powered Generation**: Uses GPT-4 to create compelling marketing copy
- ⚡ **Real-time Streaming**: Watch your brochure generate live
- 📱 **Fully Responsive**: Perfect on all devices

### Advanced Features

1. **QR Code Generation** - Automatic QR codes for website and contact info
2. **Logo Extraction** - Intelligently finds and displays company logos
3. **Image Galleries** - Extracts and showcases company images
4. **Brand Color Detection** - Matches your company's color scheme
5. **Social Media Integration** - Auto-detects all social media links
6. **Multiple Templates** - Professional, Creative, Tech, and Minimal styles
7. **Animation Options** - Fade, Slide, Zoom, or No animations
8. **PDF Export** - Professional print-ready PDFs
9. **Interactive HTML** - Fully functional, standalone HTML brochures
10. **Multiple Download Formats** - Markdown, HTML, Interactive HTML, PDF

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/brochure-generator.git
cd brochure-generator
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create `.env` file**

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

5. **Run the application**

```bash
python app.py
```

6. **Open browser**

```
http://localhost:5000
```

## 💻 Usage

### Web Interface

1. Choose a template style (Professional, Creative, Tech, Minimal)
2. Select animation style (Fade, Slide, Zoom, None)
3. Enter company name and website URL
4. Click "Generate Brochure"
5. Preview, download, or share your brochure!

### Command Line

```bash
python main.py "Company Name" "https://company.com" --stream
```

**Options:**

- `--stream` or `-s`: Enable streaming mode
- `--output` or `-o`: Specify output filename
- `--model` or `-m`: Choose AI model

## 📦 Project Structure
