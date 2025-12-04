# import os
# import json
# from dotenv import load_dotenv
# from openai import OpenAI
# from scraper import fetch_website_links, fetch_website_contents
# import qrcode
# from io import BytesIO
# import base64
# from PIL import Image
# import requests
# from colorthief import ColorThief
# import re
# from urllib.parse import urljoin, urlparse


# class BrochureGenerator:
#     def __init__(self, model="gpt-4o-mini"):
#         """
#         Initialize the Brochure Generator with OpenAI API
        
#         Args:
#             model: The OpenAI model to use (default: gpt-4o-mini)
#         """
#         load_dotenv(override=True)
#         api_key = os.getenv('OPENAI_API_KEY')
        
#         # Better error messages
#         if not api_key:
#             raise ValueError(
#                 "OPENAI_API_KEY not found in .env file!\n"
#                 "Please create a .env file with: OPENAI_API_KEY=your-key-here"
#             )
        
#         if not api_key.startswith('sk-'):
#             raise ValueError(
#                 f"Invalid API key format. Key should start with 'sk-' but got: {api_key[:10]}...\n"
#                 "Please check your .env file."
#             )
        
#         print(f"✅ API Key loaded successfully (length: {len(api_key)})")
        
#         self.openai = OpenAI(api_key=api_key)
#         self.model = model
#         self.link_selection_model = "gpt-4o-mini"
        
#         self.link_system_prompt = """
# You are provided with a list of links found on a webpage.
# You are able to decide which of the links would be most relevant to include in a brochure about the company,
# such as links to an About page, or a Company page, or Careers/Jobs pages.
# You should respond in JSON as in this example:

# {
#     "links": [
#         {"type": "about page", "url": "https://full.url/goes/here/about"},
#         {"type": "careers page", "url": "https://another.full.url/careers"}
#     ]
# }
# """
        
#         self.brochure_system_prompt = """
# You are an expert marketing copywriter and brochure designer creating professional marketing materials.

# Your task is to create a compelling, visually-structured company brochure that would be used by:
# - Sales teams to pitch to clients
# - Investors for funding decisions  
# - Job seekers to learn about the company
# - Partners for collaboration opportunities

# STRUCTURE YOUR BROCHURE WITH THESE SECTIONS:

# ## Executive Summary
# [2-3 compelling sentences that capture the company's essence and unique value proposition]

# ## About [Company Name]
# [Rich description of the company, its mission, vision, and what makes it special]

# ## What We Do
# [Clear explanation of products/services with benefits focus]

# ## Our Solutions
# [Bullet points of key offerings, each with a brief benefit statement]

# ## Who We Serve
# [Target markets, customer types, industries served]

# ## Why Choose Us?
# [Unique selling points, competitive advantages, key differentiators]

# ## By The Numbers
# [If available: statistics, metrics, achievements, milestones - format as bullet points]

# ## Our Customers
# [If available: customer names, case studies, testimonials]

# ## Recognition & Awards
# [If available: awards, certifications, partnerships]

# ## Company Culture
# [If available: values, work environment, team culture]

# ## Career Opportunities
# [If available: why work here, open positions, benefits]

# ## 📞 Get In Touch
# [Contact information and call-to-action]

# WRITING GUIDELINES:
# - Use engaging, benefit-focused language
# - Keep paragraphs concise (2-4 sentences max)
# - Use bullet points for easy scanning
# - Include specific numbers and metrics when available
# - Write in an enthusiastic but professional tone
# - Focus on outcomes and value, not just features
# - Use action-oriented language
# - Make it skimmable with clear headings and structure

# FORMATTING:
# - Use emojis for visual interest in headings
# - Bold important points
# - Use ">" for quote-style callouts when highlighting key information
# - Create clear visual hierarchy with headers
# - Add horizontal rules (---) to separate major sections

# OUTPUT: Return ONLY the brochure content in markdown format. Do not include code blocks or explanations.
# """

#     def get_links_user_prompt(self, url):
#         """Create a user prompt for selecting relevant links"""
#         user_prompt = f"""
# Here is the list of links on the website {url} -
# Please decide which of these are relevant web links for a brochure about the company, 
# respond with the full https URL in JSON format.
# Do not include Terms of Service, Privacy, email links.

# Links (some might be relative links):

# """
#         links = fetch_website_links(url)
#         user_prompt += "\n".join(links)
#         return user_prompt

#     def select_relevant_links(self, url):
#         """Use AI to select relevant links from a webpage"""
#         print(f"🔍 Selecting relevant links for {url}...")
        
#         try:
#             response = self.openai.chat.completions.create(
#                 model=self.link_selection_model,
#                 messages=[
#                     {"role": "system", "content": self.link_system_prompt},
#                     {"role": "user", "content": self.get_links_user_prompt(url)}
#                 ],
#                 response_format={"type": "json_object"}
#             )
            
#             result = response.choices[0].message.content
#             links = json.loads(result)
#             print(f"✅ Found {len(links.get('links', []))} relevant links")
#             return links
#         except Exception as e:
#             print(f"❌ Error selecting links: {e}")
#             return {"links": []}

#     def fetch_page_and_all_relevant_links(self, url):
#         """Fetch main page content and all relevant linked pages"""
#         print(f"📄 Fetching main page content...")
#         contents = fetch_website_contents(url)
#         relevant_links = self.select_relevant_links(url)
        
#         result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
        
#         for link in relevant_links.get('links', []):
#             try:
#                 print(f"📄 Fetching {link['type']}: {link['url']}")
#                 result += f"\n\n### Link: {link['type']}\n"
#                 result += fetch_website_contents(link["url"])
#             except Exception as e:
#                 print(f"⚠️  Could not fetch {link['url']}: {e}")
#                 continue
        
#         return result

#     def get_brochure_user_prompt(self, company_name, url):
#         """Create the user prompt for brochure generation"""
#         user_prompt = f"""
# You are looking at a company called: {company_name}
# Here are the contents of its landing page and other relevant pages;
# use this information to build a short brochure of the company in markdown without code blocks.

# """
#         user_prompt += self.fetch_page_and_all_relevant_links(url)
#         user_prompt = user_prompt[:15_000]
#         return user_prompt

#     def create_brochure(self, company_name, url):
#         """Generate a brochure for the company (non-streaming)"""
#         print(f"\n🎨 Generating brochure for {company_name}...\n")
        
#         try:
#             response = self.openai.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": self.brochure_system_prompt},
#                     {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
#                 ],
#             )
            
#             result = response.choices[0].message.content
#             print("\n✅ Brochure generated successfully!\n")
#             return result
#         except Exception as e:
#             print(f"\n❌ Error generating brochure: {e}\n")
#             return None

#     def stream_brochure(self, company_name, url):
#         """Generate a brochure with streaming output (typewriter effect)"""
#         print(f"\n🎨 Generating brochure for {company_name}...\n")
#         print("-" * 80)
        
#         try:
#             stream = self.openai.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": self.brochure_system_prompt},
#                     {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
#                 ],
#                 stream=True
#             )
            
#             full_response = ""
#             for chunk in stream:
#                 content = chunk.choices[0].delta.content or ''
#                 full_response += content
#                 print(content, end='', flush=True)
#                 yield content
            
#             print("\n" + "-" * 80)
#             print("\n✅ Brochure generated successfully!\n")
#             return full_response
            
#         except Exception as e:
#             print(f"\n❌ Error generating brochure: {e}\n")
#             return None

#     def save_brochure(self, brochure_content, filename):
#         """Save brochure content to a file"""
#         try:
#             with open(filename, 'w', encoding='utf-8') as f:
#                 f.write(brochure_content)
#             print(f"💾 Brochure saved to {filename}")
#         except Exception as e:
#             print(f"❌ Error saving brochure: {e}")
    
#     # ========================================
#     # FEATURE 1: QR Code Generation
#     # ========================================
    
#     def generate_qr_code(self, data, size=200):
#         """
#         Generate QR code for contact information or URL
        
#         Args:
#             data: String data to encode (URL, vCard, etc.)
#             size: Size of QR code in pixels
            
#         Returns:
#             Base64 encoded image string
#         """
#         try:
#             qr = qrcode.QRCode(
#                 version=1,
#                 error_correction=qrcode.constants.ERROR_CORRECT_H,
#                 box_size=10,
#                 border=4,
#             )
#             qr.add_data(data)
#             qr.make(fit=True)
            
#             img = qr.make_image(fill_color="#6366f1", back_color="white")
#             img = img.resize((size, size), Image.Resampling.LANCZOS)
            
#             buffered = BytesIO()
#             img.save(buffered, format="PNG")
#             img_str = base64.b64encode(buffered.getvalue()).decode()
            
#             return f"data:image/png;base64,{img_str}"
#         except Exception as e:
#             print(f"Error generating QR code: {e}")
#             return None
    
#     def generate_vcard_qr(self, company_name, url, email="", phone=""):
#         """Generate QR code with vCard format for easy contact saving"""
#         vcard = f"""BEGIN:VCARD
# VERSION:3.0
# FN:{company_name}
# ORG:{company_name}
# URL:{url}
# EMAIL:{email}
# TEL:{phone}
# END:VCARD"""
#         return self.generate_qr_code(vcard)
    
#     # ========================================
#     # FEATURE 2: Logo Extraction
#     # ========================================
    
#     def extract_company_logo(self, url):
#         """
#         Extract company logo from website
        
#         Args:
#             url: Company website URL
            
#         Returns:
#             Base64 encoded logo image or None
#         """
#         try:
#             from bs4 import BeautifulSoup
            
#             response = requests.get(url, timeout=10, headers={
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             })
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Try different methods to find logo
#             logo_url = None
            
#             # Method 1: Look for logo in meta tags
#             meta_image = soup.find('meta', property='og:image')
#             if meta_image and meta_image.get('content'):
#                 logo_url = meta_image['content']
            
#             # Method 2: Look for common logo selectors
#             if not logo_url:
#                 logo_selectors = [
#                     'img[class*="logo" i]',
#                     'img[id*="logo" i]',
#                     'a.logo img',
#                     '.header img',
#                     '.navbar-brand img',
#                     'img[alt*="logo" i]'
#                 ]
                
#                 for selector in logo_selectors:
#                     logo_img = soup.select_one(selector)
#                     if logo_img and logo_img.get('src'):
#                         logo_url = logo_img['src']
#                         break
            
#             # Method 3: Favicon as fallback
#             if not logo_url:
#                 favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
#                 if favicon and favicon.get('href'):
#                     logo_url = favicon['href']
            
#             if logo_url:
#                 # Make URL absolute
#                 logo_url = urljoin(url, logo_url)
                
#                 # Download and encode image
#                 img_response = requests.get(logo_url, timeout=10, headers={
#                     'User-Agent': 'Mozilla/5.0'
#                 })
                
#                 if img_response.status_code == 200:
#                     # Convert to base64
#                     img_data = base64.b64encode(img_response.content).decode()
#                     mime_type = img_response.headers.get('content-type', 'image/png')
#                     print(f"✅ Extracted company logo")
#                     return f"data:{mime_type};base64,{img_data}"
            
#             print(f"⚠️  Could not find company logo")
#             return None
            
#         except Exception as e:
#             print(f"Error extracting logo: {e}")
#             return None
    
#     # ========================================
#     # FEATURE 3: Image Gallery Extraction
#     # ========================================
    
#     def extract_company_images(self, url, max_images=6):
#         """
#         Extract high-quality images from company website
        
#         Args:
#             url: Company website URL
#             max_images: Maximum number of images to extract
            
#         Returns:
#             List of base64 encoded images
#         """
#         try:
#             from bs4 import BeautifulSoup
            
#             response = requests.get(url, timeout=10, headers={
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#             })
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             images = []
#             img_tags = soup.find_all('img')
            
#             for img in img_tags:
#                 if len(images) >= max_images:
#                     break
                
#                 img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
#                 if not img_url:
#                     continue
                
#                 # Skip small images, icons, logos
#                 width = img.get('width')
#                 height = img.get('height')
                
#                 # Skip if obviously small
#                 if width and height:
#                     try:
#                         if int(width) < 200 or int(height) < 200:
#                             continue
#                     except:
#                         pass
                
#                 # Skip common icon patterns
#                 skip_patterns = ['icon', 'logo', 'favicon', 'sprite', 'avatar', 'thumb']
#                 if any(x in img_url.lower() for x in skip_patterns):
#                     continue
                
#                 # Skip SVG files
#                 if img_url.lower().endswith('.svg'):
#                     continue
                
#                 try:
#                     # Make URL absolute
#                     img_url = urljoin(url, img_url)
                    
#                     # Download image
#                     img_response = requests.get(img_url, timeout=5, headers={
#                         'User-Agent': 'Mozilla/5.0'
#                     })
                    
#                     if img_response.status_code == 200:
#                         # Check actual image size
#                         img_data = BytesIO(img_response.content)
#                         with Image.open(img_data) as pil_img:
#                             if pil_img.width >= 300 and pil_img.height >= 200:
#                                 # Resize if too large
#                                 if pil_img.width > 800:
#                                     pil_img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                                
#                                 # Convert to base64
#                                 buffered = BytesIO()
#                                 pil_img.convert('RGB').save(buffered, format="JPEG", quality=85)
#                                 img_str = base64.b64encode(buffered.getvalue()).decode()
#                                 images.append(f"data:image/jpeg;base64,{img_str}")
                
#                 except Exception as e:
#                     continue
            
#             print(f"✅ Extracted {len(images)} images")
#             return images
            
#         except Exception as e:
#             print(f"Error extracting images: {e}")
#             return []
    
#     # ========================================
#     # FEATURE 4: Brand Color Extraction
#     # ========================================
    
#     def extract_brand_colors(self, url, logo_data=None):
#         """
#         Extract brand colors from company website or logo
        
#         Args:
#             url: Company website URL
#             logo_data: Base64 logo data (optional)
            
#         Returns:
#             Dict with primary, secondary, accent colors
#         """
#         try:
#             colors = {
#                 'primary': '#6366f1',
#                 'secondary': '#ec4899',
#                 'accent': '#8b5cf6'
#             }
            
#             # Try to extract from logo if provided
#             if logo_data and logo_data.startswith('data:image'):
#                 try:
#                     # Decode base64 image
#                     img_data = base64.b64decode(logo_data.split(',')[1])
#                     img_file = BytesIO(img_data)
                    
#                     # Get dominant color
#                     color_thief = ColorThief(img_file)
#                     dominant_color = color_thief.get_color(quality=1)
#                     palette = color_thief.get_palette(color_count=3, quality=1)
                    
#                     # Convert to hex
#                     colors['primary'] = '#{:02x}{:02x}{:02x}'.format(*dominant_color)
#                     colors['secondary'] = '#{:02x}{:02x}{:02x}'.format(*palette[1])
#                     colors['accent'] = '#{:02x}{:02x}{:02x}'.format(*palette[2])
                    
#                     print(f"✅ Extracted brand colors from logo")
#                     return colors
#                 except Exception as e:
#                     print(f"Could not extract colors from logo: {e}")
            
#             # Fallback: Try to extract from CSS
#             try:
#                 from bs4 import BeautifulSoup
#                 response = requests.get(url, timeout=10)
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for CSS variables or inline styles
#                 style_tags = soup.find_all('style')
#                 for style in style_tags:
#                     content = style.string
#                     if content:
#                         # Look for color definitions
#                         hex_colors = re.findall(r'#[0-9a-fA-F]{6}', content)
#                         if len(hex_colors) >= 3:
#                             colors['primary'] = hex_colors[0]
#                             colors['secondary'] = hex_colors[1]
#                             colors['accent'] = hex_colors[2]
#                             print(f"✅ Extracted brand colors from CSS")
#                             return colors
#             except:
#                 pass
            
#             print(f"⚠️  Using default brand colors")
#             return colors
            
#         except Exception as e:
#             print(f"Error extracting colors: {e}")
#             return {
#                 'primary': '#6366f1',
#                 'secondary': '#ec4899',
#                 'accent': '#8b5cf6'
#             }
    
#     # ========================================
#     # FEATURE 5: Social Media Extraction
#     # ========================================
    
#     def extract_social_media(self, url):
#         """
#         Extract social media links from company website
        
#         Args:
#             url: Company website URL
            
#         Returns:
#             Dict with social media platforms and URLs
#         """
#         try:
#             from bs4 import BeautifulSoup
            
#             response = requests.get(url, timeout=10, headers={
#                 'User-Agent': 'Mozilla/5.0'
#             })
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             social_media = {}
            
#             social_patterns = {
#                 'linkedin': ['linkedin.com', 'fa-linkedin', 'linkedin'],
#                 'twitter': ['twitter.com', 'x.com', 'fa-twitter', 'fa-x-twitter'],
#                 'facebook': ['facebook.com', 'fa-facebook', 'fb.com'],
#                 'instagram': ['instagram.com', 'fa-instagram'],
#                 'youtube': ['youtube.com', 'youtu.be', 'fa-youtube'],
#                 'github': ['github.com', 'fa-github']
#             }
            
#             # Find all links
#             links = soup.find_all('a', href=True)
            
#             for link in links:
#                 href = link['href'].lower()
                
#                 for platform, patterns in social_patterns.items():
#                     if any(pattern in href for pattern in patterns):
#                         if platform not in social_media:
#                             # Clean up the URL
#                             if not href.startswith('http'):
#                                 href = 'https://' + href
#                             social_media[platform] = href
            
#             print(f"✅ Found {len(social_media)} social media links")
#             return social_media
            
#         except Exception as e:
#             print(f"Error extracting social media: {e}")
#             return {}
    
#     # ========================================
#     # FEATURE 6: Generate Interactive HTML
#     # ========================================
    
#     def generate_interactive_html(self, brochure_content, company_name, company_url="", 
#                                   animation_style="fade", template_style="professional"):
#         """
#         Generate an interactive, professionally designed HTML brochure with all enhancements
        
#         Args:
#             brochure_content: Markdown content of the brochure
#             company_name: Name of the company
#             company_url: Company website URL (optional)
#             animation_style: Animation style (fade, slide, zoom, none)
#             template_style: Template style (professional, creative, tech, minimal)
            
#         Returns:
#             HTML string with professional design
#         """
#         import markdown
        
#         print(f"🎨 Generating interactive HTML brochure...")
        
#         # Extract company assets
#         logo_data = None
#         images = []
#         social_media = {}
#         brand_colors = {
#             'primary': '#6366f1',
#             'secondary': '#ec4899',
#             'accent': '#8b5cf6'
#         }
        
#         if company_url:
#             print(f"📸 Extracting company assets from {company_url}...")
#             logo_data = self.extract_company_logo(company_url)
#             images = self.extract_company_images(company_url, max_images=6)
#             social_media = self.extract_social_media(company_url)
#             brand_colors = self.extract_brand_colors(company_url, logo_data)
        
#         # Generate QR codes
#         qr_url = self.generate_qr_code(company_url) if company_url else None
#         qr_vcard = self.generate_vcard_qr(company_name, company_url) if company_url else None
        
#         # Convert markdown to HTML
#         html_content = markdown.markdown(
#             brochure_content,
#             extensions=['extra', 'codehilite', 'nl2br', 'tables']
#         )
        
#         # Get template-specific colors
#         if template_style == "creative":
#             brand_colors = {
#                 'primary': '#ff6b6b',
#                 'secondary': '#4ecdc4',
#                 'accent': '#ffe66d'
#             }
#         elif template_style == "tech":
#             brand_colors = {
#                 'primary': '#00d9ff',
#                 'secondary': '#7c3aed',
#                 'accent': '#10b981'
#             }
#         elif template_style == "minimal":
#             brand_colors = {
#                 'primary': '#1e293b',
#                 'secondary': '#64748b',
#                 'accent': '#94a3b8'
#             }
        
#         # Animation styles
#         animation_css = ""
#         if animation_style == "fade":
#             animation_css = """
#             @keyframes fadeInUp {
#                 from { opacity: 0; transform: translateY(30px); }
#                 to { opacity: 1; transform: translateY(0); }
#             }
#             .animated { animation: fadeInUp 0.8s ease-out; }
#             """
#         elif animation_style == "slide":
#             animation_css = """
#             @keyframes slideInLeft {
#                 from { opacity: 0; transform: translateX(-50px); }
#                 to { opacity: 1; transform: translateX(0); }
#             }
#             @keyframes slideInRight {
#                 from { opacity: 0; transform: translateX(50px); }
#                 to { opacity: 1; transform: translateX(0); }
#             }
#             .animated:nth-child(odd) { animation: slideInLeft 0.8s ease-out; }
#             .animated:nth-child(even) { animation: slideInRight 0.8s ease-out; }
#             """
#         elif animation_style == "zoom":
#             animation_css = """
#             @keyframes zoomIn {
#                 from { opacity: 0; transform: scale(0.8); }
#                 to { opacity: 1; transform: scale(1); }
#             }
#             .animated { animation: zoomIn 0.6s ease-out; }
#             """
        
#         # Build image gallery HTML
#         gallery_html = ""
#         if images:
#             gallery_html = '<div class="image-gallery">'
#             for i, img in enumerate(images[:6]):
#                 gallery_html += f'''
#                 <div class="gallery-item animated" style="animation-delay: {i * 0.1}s;">
#                     <img src="{img}" alt="Company Image {i+1}">
#                 </div>
#                 '''
#             gallery_html += '</div>'
        
#         # Build social media HTML
#         social_html = ""
#         if social_media:
#             social_icons = {
#                 'linkedin': 'fa-linkedin-in',
#                 'twitter': 'fa-x-twitter',
#                 'facebook': 'fa-facebook-f',
#                 'instagram': 'fa-instagram',
#                 'youtube': 'fa-youtube',
#                 'github': 'fa-github'
#             }
#             social_html = '<div class="social-links">'
#             for platform, url in social_media.items():
#                 icon = social_icons.get(platform, 'fa-link')
#                 social_html += f'''
#                 <a href="{url}" target="_blank" rel="noopener" title="{platform.title()}">
#                     <i class="fab {icon}"></i>
#                 </a>
#                 '''
#             social_html += '</div>'
        
#         # QR codes section
#         qr_section = ""
#         if qr_url or qr_vcard:
#             qr_section = '<div class="qr-section animated">'
#             qr_section += '<h3>📱 Quick Access</h3>'
#             qr_section += '<div class="qr-codes">'
#             if qr_url:
#                 qr_section += f'''
#                 <div class="qr-code-item">
#                     <img src="{qr_url}" alt="Website QR Code">
#                     <p>Scan to visit website</p>
#                 </div>
#                 '''
#             if qr_vcard:
#                 qr_section += f'''
#                 <div class="qr-code-item">
#                     <img src="{qr_vcard}" alt="Contact QR Code">
#                     <p>Scan to save contact</p>
#                 </div>
#                 '''
#             qr_section += '</div></div>'
        
#         # Generate complete HTML
#         return f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{company_name} - Professional Brochure</title>
#     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
#     <style>
#         * {{
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }}
        
#         :root {{
#             --primary: {brand_colors['primary']};
#             --secondary: {brand_colors['secondary']};
#             --accent: {brand_colors['accent']};
#             --dark: #1e293b;
#             --gray: #64748b;
#             --light: #f1f5f9;
#             --white: #ffffff;
#         }}
        
#         body {{
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             line-height: 1.8;
#             color: var(--dark);
#             background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
#             padding: 0;
#             margin: 0;
#         }}
        
#         .page-wrapper {{
#             max-width: 1200px;
#             margin: 0 auto;
#             padding: 40px 20px;
#         }}
        
#         .brochure-header {{
#             background: white;
#             padding: 60px 40px;
#             border-radius: 20px;
#             box-shadow: 0 20px 60px rgba(0,0,0,0.3);
#             text-align: center;
#             margin-bottom: 40px;
#             position: relative;
#             overflow: hidden;
#         }}
        
#         .brochure-header::before {{
#             content: '';
#             position: absolute;
#             top: 0;
#             left: 0;
#             right: 0;
#             height: 5px;
#             background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
#         }}
        
#         .company-logo {{
#             width: 150px;
#             height: 150px;
#             margin: 0 auto 20px;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             border-radius: 50%;
#             overflow: hidden;
#             box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
#             background: white;
#         }}
        
#         .company-logo img {{
#             max-width: 100%;
#             max-height: 100%;
#             object-fit: contain;
#         }}
        
#         .company-logo-fallback {{
#             background: linear-gradient(135deg, var(--primary), var(--accent));
#             color: white;
#             font-size: 48px;
#             font-weight: bold;
#             width: 100%;
#             height: 100%;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#         }}
#         .brochure-header h1 {{
#             font-size: 3rem;
#             color: var(--dark);
#             margin-bottom: 15px;
#             font-weight: 800;
#         }}
        
#         .brochure-subtitle {{
#             font-size: 1.3rem;
#             color: var(--gray);
#             margin-bottom: 20px;
#         }}
        
#         .header-badge {{
#             display: inline-block;
#             background: linear-gradient(135deg, var(--primary), var(--accent));
#             color: white;
#             padding: 10px 25px;
#             border-radius: 50px;
#             font-weight: 600;
#             font-size: 0.9rem;
#             margin: 10px 5px;
#         }}
        
#         .image-gallery {{
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
#             gap: 20px;
#             margin: 40px 0;
#             padding: 0;
#         }}
        
#         .gallery-item {{
#             border-radius: 15px;
#             overflow: hidden;
#             box-shadow: 0 10px 30px rgba(0,0,0,0.2);
#             transition: transform 0.3s ease;
#         }}
        
#         .gallery-item:hover {{
#             transform: translateY(-10px) scale(1.02);
#         }}
        
#         .gallery-item img {{
#             width: 100%;
#             height: 200px;
#             object-fit: cover;
#             display: block;
#         }}
        
#         .brochure-content {{
#             background: white;
#             padding: 60px;
#             border-radius: 20px;
#             box-shadow: 0 20px 60px rgba(0,0,0,0.3);
#             margin-bottom: 40px;
#         }}
        
#         .brochure-content h2 {{
#             color: var(--primary);
#             font-size: 2.2rem;
#             margin-top: 50px;
#             margin-bottom: 25px;
#             padding-bottom: 15px;
#             border-bottom: 3px solid var(--primary);
#             position: relative;
#         }}
        
#         .brochure-content h2:first-child {{
#             margin-top: 0;
#         }}
        
#         .brochure-content h2::after {{
#             content: '';
#             position: absolute;
#             bottom: -3px;
#             left: 0;
#             width: 100px;
#             height: 3px;
#             background: var(--secondary);
#         }}
        
#         .brochure-content h3 {{
#             color: var(--accent);
#             font-size: 1.6rem;
#             margin-top: 35px;
#             margin-bottom: 15px;
#         }}
        
#         .brochure-content p {{
#             margin-bottom: 20px;
#             font-size: 1.1rem;
#             line-height: 1.8;
#         }}
        
#         .brochure-content ul,
#         .brochure-content ol {{
#             margin-left: 30px;
#             margin-bottom: 25px;
#         }}
        
#         .brochure-content li {{
#             margin-bottom: 12px;
#             font-size: 1.05rem;
#             line-height: 1.7;
#         }}
        
#         .brochure-content li::marker {{
#             color: var(--primary);
#             font-weight: bold;
#         }}
        
#         .brochure-content blockquote {{
#             background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
#             border-left: 5px solid var(--primary);
#             padding: 25px 30px;
#             margin: 30px 0;
#             border-radius: 10px;
#             font-style: italic;
#             font-size: 1.15rem;
#         }}
        
#         .brochure-content strong {{
#             color: var(--primary);
#             font-weight: 700;
#         }}
        
#         .brochure-content a {{
#             color: var(--primary);
#             text-decoration: none;
#             border-bottom: 2px solid var(--primary);
#             transition: all 0.3s ease;
#         }}
        
#         .brochure-content a:hover {{
#             color: var(--secondary);
#             border-bottom-color: var(--secondary);
#         }}
        
#         .brochure-content hr {{
#             border: none;
#             height: 2px;
#             background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
#             margin: 50px 0;
#         }}
        
#         .qr-section {{
#             background: var(--light);
#             padding: 40px;
#             border-radius: 15px;
#             margin: 40px 0;
#             text-align: center;
#         }}
        
#         .qr-section h3 {{
#             margin-top: 0;
#             margin-bottom: 30px;
#             color: var(--primary);
#         }}
        
#         .qr-codes {{
#             display: flex;
#             justify-content: center;
#             gap: 40px;
#             flex-wrap: wrap;
#         }}
        
#         .qr-code-item {{
#             background: white;
#             padding: 20px;
#             border-radius: 15px;
#             box-shadow: 0 5px 15px rgba(0,0,0,0.1);
#             transition: transform 0.3s ease;
#         }}
        
#         .qr-code-item:hover {{
#             transform: translateY(-5px);
#         }}
        
#         .qr-code-item img {{
#             width: 200px;
#             height: 200px;
#             display: block;
#             margin-bottom: 15px;
#         }}
        
#         .qr-code-item p {{
#             margin: 0;
#             color: var(--gray);
#             font-weight: 600;
#         }}
        
#         .brochure-footer {{
#             background: white;
#             padding: 50px 40px;
#             border-radius: 20px;
#             box-shadow: 0 20px 60px rgba(0,0,0,0.3);
#             text-align: center;
#         }}
        
#         .cta-button {{
#             display: inline-block;
#             background: linear-gradient(135deg, var(--primary), var(--accent));
#             color: white;
#             padding: 18px 40px;
#             border-radius: 50px;
#             text-decoration: none;
#             font-weight: 700;
#             font-size: 1.2rem;
#             margin: 20px 10px;
#             box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
#             transition: all 0.3s ease;
#         }}
        
#         .cta-button:hover {{
#             transform: translateY(-3px);
#             box-shadow: 0 15px 40px rgba(99, 102, 241, 0.4);
#         }}
        
#         .social-links {{
#             margin-top: 30px;
#             display: flex;
#             justify-content: center;
#             gap: 15px;
#             flex-wrap: wrap;
#         }}
        
#         .social-links a {{
#             display: inline-flex;
#             align-items: center;
#             justify-content: center;
#             width: 50px;
#             height: 50px;
#             background: var(--light);
#             border-radius: 50%;
#             color: var(--primary);
#             font-size: 1.3rem;
#             transition: all 0.3s ease;
#             text-decoration: none;
#         }}
        
#         .social-links a:hover {{
#             background: var(--primary);
#             color: white;
#             transform: translateY(-3px);
#         }}
        
#         {animation_css}
        
#         @media print {{
#             body {{ background: white; }}
#             .page-wrapper {{ padding: 0; }}
#             .brochure-header, .brochure-content, .brochure-footer {{
#                 box-shadow: none;
#                 page-break-inside: avoid;
#             }}
#             .cta-button {{ display: none; }}
#         }}
        
#         @media (max-width: 768px) {{
#             .brochure-header {{ padding: 40px 20px; }}
#             .brochure-header h1 {{ font-size: 2rem; }}
#             .brochure-content {{ padding: 30px 20px; }}
#             .brochure-content h2 {{ font-size: 1.8rem; }}
#             .image-gallery {{ grid-template-columns: 1fr; }}
#             .qr-codes {{ flex-direction: column; align-items: center; }}
#         }}
        
#         html {{ scroll-behavior: smooth; }}
#     </style>
# </head>
# <body>
#     <div class="page-wrapper">
#         <header class="brochure-header animated">
#             <div class="company-logo">
#                 {f'<img src="{logo_data}" alt="{company_name} Logo">' if logo_data else f'<div class="company-logo-fallback">{company_name[0].upper()}</div>'}
#             </div>
#             <h1>{company_name}</h1>
#             <p class="brochure-subtitle">Professional Company Brochure</p>
#             <div class="header-badge">📄 Marketing Material</div>
#             {f'<div class="header-badge">🌐 <a href="{company_url}" style="color: white; text-decoration: none;">{company_url}</a></div>' if company_url else ''}
#         </header>
        
#         {gallery_html}
        
#         <main class="brochure-content animated">
#             {html_content}
#         </main>
        
#         {qr_section}
        
#         <footer class="brochure-footer animated">
#             <h2>Ready to Connect?</h2>
#             <p style="font-size: 1.2rem; color: var(--gray); margin: 20px 0;">
#                 Get in touch with us today to discover how we can help you achieve your goals.
#             </p>
#             {f'<a href="{company_url}" class="cta-button">🌐 Visit Website</a>' if company_url else ''}
#             <a href="javascript:window.print()" class="cta-button">📄 Print Brochure</a>
            
#             {social_html}
            
#             <p style="margin-top: 40px; color: var(--gray); font-size: 0.9rem;">
#                 Generated by AI Brochure Generator | © {company_name}
#             </p>
#         </footer>
#     </div>
    
#     <script>
#         const observerOptions = {{
#             threshold: 0.1,
#             rootMargin: '0px 0px -100px 0px'
#         }};
        
#         const observer = new IntersectionObserver((entries) => {{
#             entries.forEach(entry => {{
#                 if (entry.isIntersecting) {{
#                     entry.target.classList.add('animated');
#                 }}
#             }});
#         }}, observerOptions);
        
#         document.querySelectorAll('.gallery-item, .qr-section').forEach(el => {{
#             observer.observe(el);
#         }});
#     </script>
# </body>
# </html>"""
    
#     # ========================================
#     # FEATURE 7: PDF Export
#     # ========================================
    
#     def generate_pdf_brochure(self, brochure_content, company_name, company_url=""):
#         """
#         Generate a professional PDF brochure
        
#         Args:
#             brochure_content: Markdown content
#             company_name: Company name
#             company_url: Company URL
            
#         Returns:
#             PDF bytes
#         """
#         try:
#             from reportlab.lib.pagesizes import letter
#             from reportlab.lib.units import inch
#             from reportlab.lib import colors
#             from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
#             from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#             from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
            
#             buffer = BytesIO()
            
#             doc = SimpleDocTemplate(
#                 buffer,
#                 pagesize=letter,
#                 rightMargin=72,
#                 leftMargin=72,
#                 topMargin=72,
#                 bottomMargin=72
#             )
            
#             story = []
#             styles = getSampleStyleSheet()
            
#             title_style = ParagraphStyle(
#                 'CustomTitle',
#                 parent=styles['Heading1'],
#                 fontSize=32,
#                 textColor=colors.HexColor('#6366f1'),
#                 spaceAfter=30,
#                 alignment=TA_CENTER,
#                 fontName='Helvetica-Bold'
#             )
            
#             heading_style = ParagraphStyle(
#                 'CustomHeading',
#                 parent=styles['Heading2'],
#                 fontSize=18,
#                 textColor=colors.HexColor('#6366f1'),
#                 spaceAfter=12,
#                 spaceBefore=20,
#                 fontName='Helvetica-Bold'
#             )
            
#             body_style = ParagraphStyle(
#                 'CustomBody',
#                 parent=styles['BodyText'],
#                 fontSize=11,
#                 alignment=TA_JUSTIFY,
#                 spaceAfter=12
#             )
            
#             story.append(Paragraph(company_name, title_style))
#             story.append(Spacer(1, 0.3*inch))
            
#             subtitle = Paragraph("Professional Company Brochure", styles['Normal'])
#             story.append(subtitle)
#             story.append(Spacer(1, 0.5*inch))
            
#             lines = brochure_content.split('\n')
#             for line in lines:
#                 line = line.strip()
#                 if not line:
#                     story.append(Spacer(1, 0.1*inch))
#                     continue
                
#                 if line.startswith('## '):
#                     text = line[3:].strip()
#                     # Remove emojis from text
#                     text = re.sub(r'[^\x00-\x7F]+', '', text)
#                     if text.strip():
#                         story.append(Paragraph(text, heading_style))
#                 elif line.startswith('# '):
#                     text = line[2:].strip()
#                     text = re.sub(r'[^\x00-\x7F]+', '', text)
#                     if text.strip():
#                         story.append(Paragraph(text, title_style))
#                 elif line.startswith('- ') or line.startswith('* '):
#                     text = '• ' + line[2:].strip()
#                     text = re.sub(r'[^\x00-\x7F]+', '', text)
#                     if text.strip():
#                         story.append(Paragraph(text, body_style))
#                 elif line[0].isdigit() and '. ' in line:
#                     text = re.sub(r'[^\x00-\x7F]+', '', line)
#                     if text.strip():
#                         story.append(Paragraph(text, body_style))
#                 else:
#                     clean_line = re.sub(r'[^\x00-\x7F]+', '', line)
#                     if clean_line.strip():
#                         story.append(Paragraph(clean_line, body_style))
            
#             story.append(Spacer(1, 0.5*inch))
#             if company_url:
#                 footer_text = f"Visit us at: {company_url}"
#                 story.append(Paragraph(footer_text, styles['Normal']))
            
#             doc.build(story)
            
#             pdf_bytes = buffer.getvalue()
#             buffer.close()
            
#             print(f"✅ Generated PDF brochure")
#             return pdf_bytes
            
#         except Exception as e:
#             print(f"Error generating PDF: {e}")
#             import traceback
#             traceback.print_exc()
#             return None
    

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents
import qrcode
from io import BytesIO
import base64
from PIL import Image
import requests
from colorthief import ColorThief
import re
from urllib.parse import urljoin, urlparse


class BrochureGenerator:
    def __init__(self, model="gpt-4o-mini"):
        """
        Initialize the Brochure Generator with OpenAI API
        
        Args:
            model: The OpenAI model to use (default: gpt-4o-mini)
        """
        load_dotenv(override=True)
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Better error messages
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in .env file!\n"
                "Please create a .env file with: OPENAI_API_KEY=your-key-here"
            )
        
        if not api_key.startswith('sk-'):
            raise ValueError(
                f"Invalid API key format. Key should start with 'sk-' but got: {api_key[:10]}...\n"
                "Please check your .env file."
            )
        
        print(f"✅ API Key loaded successfully (length: {len(api_key)})")
        
        self.openai = OpenAI(api_key=api_key)
        self.model = model
        self.link_selection_model = "gpt-4o-mini"
        
        self.link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""
        
        self.brochure_system_prompt = """
You are an expert marketing copywriter and brochure designer creating professional marketing materials.

Your task is to create a compelling, visually-structured company brochure that would be used by:
- Sales teams to pitch to clients
- Investors for funding decisions  
- Job seekers to learn about the company
- Partners for collaboration opportunities

STRUCTURE YOUR BROCHURE WITH THESE SECTIONS:

## Executive Summary
[2-3 compelling sentences that capture the company's essence and unique value proposition]

## About [Company Name]
[Rich description of the company, its mission, vision, and what makes it special]

## What We Do
[Clear explanation of products/services with benefits focus]

## Our Solutions
[Bullet points of key offerings, each with a brief benefit statement]

## Who We Serve
[Target markets, customer types, industries served]

## Why Choose Us?
[Unique selling points, competitive advantages, key differentiators]

## By The Numbers
[If available: statistics, metrics, achievements, milestones - format as bullet points]

## Our Customers
[If available: customer names, case studies, testimonials]

## Recognition & Awards
[If available: awards, certifications, partnerships]

## Company Culture
[If available: values, work environment, team culture]

## Career Opportunities
[If available: why work here, open positions, benefits]

## 📞 Get In Touch
[Contact information and call-to-action]

WRITING GUIDELINES:
- Use engaging, benefit-focused language
- Keep paragraphs concise (2-4 sentences max)
- Use bullet points for easy scanning
- Include specific numbers and metrics when available
- Write in an enthusiastic but professional tone
- Focus on outcomes and value, not just features
- Use action-oriented language
- Make it skimmable with clear headings and structure

FORMATTING:
- Use emojis for visual interest in headings
- Bold important points
- Use ">" for quote-style callouts when highlighting key information
- Create clear visual hierarchy with headers
- Add horizontal rules (---) to separate major sections

OUTPUT: Return ONLY the brochure content in markdown format. Do not include code blocks or explanations.
"""

    def get_links_user_prompt(self, url):
        """Create a user prompt for selecting relevant links"""
        user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
        links = fetch_website_links(url)
        user_prompt += "\n".join(links)
        return user_prompt

    def select_relevant_links(self, url):
        """Use AI to select relevant links from a webpage"""
        print(f"🔍 Selecting relevant links for {url}...")
        
        try:
            response = self.openai.chat.completions.create(
                model=self.link_selection_model,
                messages=[
                    {"role": "system", "content": self.link_system_prompt},
                    {"role": "user", "content": self.get_links_user_prompt(url)}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            links = json.loads(result)
            print(f"✅ Found {len(links.get('links', []))} relevant links")
            return links
        except Exception as e:
            print(f"❌ Error selecting links: {e}")
            return {"links": []}

    def fetch_page_and_all_relevant_links(self, url):
        """Fetch main page content and all relevant linked pages"""
        print(f"📄 Fetching main page content...")
        contents = fetch_website_contents(url)
        relevant_links = self.select_relevant_links(url)
        
        result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
        
        for link in relevant_links.get('links', []):
            try:
                print(f"📄 Fetching {link['type']}: {link['url']}")
                result += f"\n\n### Link: {link['type']}\n"
                result += fetch_website_contents(link["url"])
            except Exception as e:
                print(f"⚠️  Could not fetch {link['url']}: {e}")
                continue
        
        return result

    def get_brochure_user_prompt(self, company_name, url):
        """Create the user prompt for brochure generation"""
        user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.

"""
        user_prompt += self.fetch_page_and_all_relevant_links(url)
        user_prompt = user_prompt[:15_000]
        return user_prompt

    def create_brochure(self, company_name, url):
        """Generate a brochure for the company (non-streaming)"""
        print(f"\n🎨 Generating brochure for {company_name}...\n")
        
        try:
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.brochure_system_prompt},
                    {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
                ],
            )
            
            result = response.choices[0].message.content
            print("\n✅ Brochure generated successfully!\n")
            return result
        except Exception as e:
            print(f"\n❌ Error generating brochure: {e}\n")
            return None

    def stream_brochure(self, company_name, url):
        """Generate a brochure with streaming output (typewriter effect)"""
        print(f"\n🎨 Generating brochure for {company_name}...\n")
        print("-" * 80)
        
        try:
            stream = self.openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.brochure_system_prompt},
                    {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ''
                full_response += content
                print(content, end='', flush=True)
                yield content
            
            print("\n" + "-" * 80)
            print("\n✅ Brochure generated successfully!\n")
            return full_response
            
        except Exception as e:
            print(f"\n❌ Error generating brochure: {e}\n")
            return None

    def save_brochure(self, brochure_content, filename):
        """Save brochure content to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(brochure_content)
            print(f"💾 Brochure saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving brochure: {e}")
    
    # ========================================
    # Color Extraction from Website
    # ========================================
    
    # ========================================
    # Color Extraction from Website
    # ========================================
    
    def extract_brand_colors(self, url):
        """
        Extract brand colors by analyzing logo and prominent website colors
        
        Args:
            url: Company website URL
            
        Returns:
            Dict with primary, secondary, accent colors
        """
        try:
            print(f"🎨 Extracting brand colors from {url}...")
            from bs4 import BeautifulSoup
            
            # Default colors
            colors = {
                'primary': '#6366f1',
                'secondary': '#ec4899',
                'accent': '#8b5cf6'
            }
            
            # First, try to extract logo
            logo_data = self.extract_company_logo(url)
            
            # If logo found, extract colors from it
            if logo_data and logo_data.startswith('data:image'):
                try:
                    print("   Extracting colors from logo...")
                    # Decode base64 image
                    img_data_base64 = logo_data.split(',')[1]
                    img_bytes = base64.b64decode(img_data_base64)
                    img_file = BytesIO(img_bytes)
                    
                    # Get dominant colors from logo using ColorThief
                    color_thief = ColorThief(img_file)
                    
                    # Get dominant color
                    dominant = color_thief.get_color(quality=1)
                    colors['primary'] = '#{:02x}{:02x}{:02x}'.format(*dominant)
                    print(f"   Primary (from logo): {colors['primary']}")
                    
                    # Get color palette
                    palette = color_thief.get_palette(color_count=5, quality=1)
                    
                    # Filter out grays and get vibrant colors
                    def is_vibrant(rgb):
                        r, g, b = rgb
                        # Not gray (colors should be different)
                        max_diff = max(abs(r-g), abs(g-b), abs(r-b))
                        if max_diff < 20:
                            return False
                        # Not too dark or too light
                        brightness = (r + g + b) / 3
                        if brightness < 30 or brightness > 240:
                            return False
                        return True
                    
                    vibrant_colors = [c for c in palette if is_vibrant(c)]
                    
                    if len(vibrant_colors) >= 2:
                        colors['secondary'] = '#{:02x}{:02x}{:02x}'.format(*vibrant_colors[1])
                        print(f"   Secondary (from logo): {colors['secondary']}")
                    
                    if len(vibrant_colors) >= 3:
                        colors['accent'] = '#{:02x}{:02x}{:02x}'.format(*vibrant_colors[2])
                        print(f"   Accent (from logo): {colors['accent']}")
                    
                    print(f"   ✅ Colors extracted from logo successfully")
                    return colors
                    
                except Exception as e:
                    print(f"   ⚠️  Could not extract colors from logo: {e}")
            
            # Fallback: Extract from website HTML/CSS
            print("   Extracting colors from website CSS...")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_colors = []
            
            # Look in style tags
            style_tags = soup.find_all('style')
            for style in style_tags:
                if style.string:
                    hex_colors = re.findall(r'#([0-9a-fA-F]{6})', style.string)
                    all_colors.extend(['#' + c.upper() for c in hex_colors])
            
            # Look in inline styles (focus on prominent elements)
            prominent_elements = soup.find_all(['header', 'nav', 'button', 'a'], limit=50)
            for element in prominent_elements:
                if element.get('style'):
                    hex_colors = re.findall(r'#([0-9a-fA-F]{6})', element['style'])
                    all_colors.extend(['#' + c.upper() for c in hex_colors])
            
            # Filter function
            def is_brand_color(color):
                hex_color = color.replace('#', '')
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                
                # Exclude white/light colors
                if r > 240 and g > 240 and b > 240:
                    return False
                
                # Exclude black/dark colors
                if r < 30 and g < 30 and b < 30:
                    return False
                
                # Exclude grays
                max_diff = max(abs(r-g), abs(g-b), abs(r-b))
                if max_diff < 25:
                    return False
                
                return True
            
            # Filter and count
            filtered_colors = [c for c in all_colors if is_brand_color(c)]
            
            if filtered_colors:
                from collections import Counter
                color_counts = Counter(filtered_colors)
                most_common = color_counts.most_common(5)
                unique_colors = [color for color, count in most_common]
                
                if len(unique_colors) >= 1:
                    colors['primary'] = unique_colors[0]
                    print(f"   Primary: {colors['primary']}")
                if len(unique_colors) >= 2:
                    colors['secondary'] = unique_colors[1]
                    print(f"   Secondary: {colors['secondary']}")
                if len(unique_colors) >= 3:
                    colors['accent'] = unique_colors[2]
                    print(f"   Accent: {colors['accent']}")
                
                print(f"   ✅ Extracted {len(unique_colors)} colors from CSS")
            else:
                print(f"   ⚠️  No brand colors found, using defaults")
            
            return colors
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'primary': '#6366f1',
                'secondary': '#ec4899',
                'accent': '#8b5cf6'
            }
        
    def extract_company_logo(self, url):
        """
        Extract company logo from website
        
        Args:
            url: Company website URL
            
        Returns:
            Base64 encoded logo image or None
        """
        try:
            print(f"🖼️  Extracting logo from {url}...")
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')
            
            logo_url = None
            
            # Method 1: Look for meta tags (og:image)
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                logo_url = meta_image['content']
                print(f"   Found logo in meta tag")
            
            # Method 2: Look for common logo selectors
            if not logo_url:
                logo_selectors = [
                    'img[class*="logo" i]',
                    'img[id*="logo" i]',
                    'img[alt*="logo" i]',
                    '.logo img',
                    '#logo img',
                    'header img',
                    '.header img',
                    'nav img',
                    '.navbar img',
                    '.navbar-brand img',
                    'a[class*="logo" i] img',
                    '[class*="brand" i] img'
                ]
                
                for selector in logo_selectors:
                    logo_img = soup.select_one(selector)
                    if logo_img and logo_img.get('src'):
                        logo_url = logo_img['src']
                        print(f"   Found logo with selector: {selector}")
                        break
            
            # Method 3: Favicon as fallback
            if not logo_url:
                favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
                if favicon and favicon.get('href'):
                    logo_url = favicon['href']
                    print(f"   Using favicon as logo")
            
            if logo_url:
                # Make URL absolute
                logo_url = urljoin(url, logo_url)
                print(f"   Logo URL: {logo_url}")
                
                # Download and encode image
                img_response = requests.get(logo_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                
                if img_response.status_code == 200:
                    # Convert to base64
                    img_data = base64.b64encode(img_response.content).decode()
                    mime_type = img_response.headers.get('content-type', 'image/png')
                    print(f"   ✅ Logo extracted successfully")
                    return f"data:{mime_type};base64,{img_data}"
            
            print(f"   ⚠️  Could not find logo")
            return None
            
        except Exception as e:
            print(f"   ❌ Error extracting logo: {e}")
            return None
    
    # ========================================
    # Generate Interactive HTML
    # ========================================
    
    def generate_interactive_html(self, brochure_content, company_name, company_url="", 
                                  animation_style="fade", template_style="professional"):
        """
        Generate an interactive, professionally designed HTML brochure
        """
        import markdown
        
        print(f"🎨 Generating interactive HTML brochure for {company_name}...")
        
        # Extract brand colors (this will also try to get the logo)
        brand_colors = self.extract_brand_colors(company_url) if company_url else {
            'primary': '#6366f1',
            'secondary': '#ec4899',
            'accent': '#8b5cf6'
        }
        
        # Extract logo separately for HTML
        logo_data = self.extract_company_logo(company_url) if company_url else None
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            brochure_content,
            extensions=['extra', 'codehilite', 'nl2br', 'tables']
        )
        
        # Logo HTML - use actual logo if available, otherwise use fallback
        if logo_data:
            logo_html = f'<div class="company-logo"><img src="{logo_data}" alt="{company_name} Logo"></div>'
        else:
            logo_html = f'<div class="company-logo-fallback">{company_name[0].upper() if company_name else "C"}</div>'
        
        # Generate complete HTML with extracted theme colors
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Professional Brochure</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --primary: {brand_colors['primary']};
            --secondary: {brand_colors['secondary']};
            --accent: {brand_colors['accent']};
            --dark: #1e293b;
            --gray: #64748b;
            --light: #f1f5f9;
            --white: #ffffff;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: var(--dark);
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            padding: 0;
            margin: 0;
        }}
        
        .page-wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .brochure-header {{
            background: white;
            padding: 60px 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .brochure-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
        }}
        
        .company-logo {{
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            background: white;
            padding: 10px;
        }}
        
        .company-logo img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        
        .company-logo-fallback {{
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            font-size: 48px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .brochure-header h1 {{
            font-size: 3rem;
            color: var(--dark);
            margin-bottom: 15px;
            font-weight: 800;
        }}
        
        .brochure-subtitle {{
            font-size: 1.3rem;
            color: var(--gray);
            margin-bottom: 20px;
        }}
        
        .header-badge {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9rem;
            margin: 10px 5px;
        }}
        
        .brochure-content {{
            background: white;
            padding: 60px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 40px;
            color: var(--dark);
        }}
        
        .brochure-content h2 {{
            color: var(--dark);
            font-size: 2.2rem;
            margin-top: 50px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--primary);
            position: relative;
            font-weight: 800;
        }}
        
        .brochure-content h2:first-child {{
            margin-top: 0;
        }}
        
        .brochure-content h2::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100px;
            height: 3px;
            background: var(--secondary);
        }}
        
        .brochure-content h3 {{
            color: var(--dark);
            font-size: 1.6rem;
            margin-top: 35px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        .brochure-content h4 {{
            color: var(--dark);
            font-size: 1.3rem;
            margin-top: 25px;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        
        .brochure-content p {{
            margin-bottom: 20px;
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--dark);
        }}
        
        .brochure-content ul,
        .brochure-content ol {{
            margin-left: 30px;
            margin-bottom: 25px;
        }}
        
        .brochure-content li {{
            margin-bottom: 12px;
            font-size: 1.05rem;
            line-height: 1.7;
            color: var(--dark);
        }}
        
        .brochure-content li::marker {{
            color: var(--primary);
            font-weight: bold;
        }}
        
        .brochure-content blockquote {{
            background: var(--light);
            border-left: 5px solid var(--primary);
            padding: 25px 30px;
            margin: 30px 0;
            border-radius: 10px;
            font-style: italic;
            font-size: 1.15rem;
            color: var(--dark);
        }}
        
        .brochure-content strong {{
            color: var(--primary);
            font-weight: 700;
        }}
        
        .brochure-content a {{
            color: var(--primary);
            text-decoration: none;
            border-bottom: 2px solid var(--primary);
            transition: all 0.3s ease;
        }}
        
        .brochure-content a:hover {{
            color: var(--secondary);
            border-bottom-color: var(--secondary);
        }}
        
        .brochure-content hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
            margin: 50px 0;
        }}
        
        .brochure-footer {{
            background: white;
            padding: 50px 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }}
        
        .brochure-footer h2 {{
            color: var(--dark);
            margin-bottom: 20px;
            font-weight: 800;
        }}
        
        .brochure-footer p {{
            color: var(--dark);
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            padding: 18px 40px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.2rem;
            margin: 20px 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}
        
        @media print {{
            body {{ background: white; }}
            .page-wrapper {{ padding: 0; }}
            .brochure-header, .brochure-content, .brochure-footer {{
                box-shadow: none;
                page-break-inside: avoid;
            }}
            .cta-button {{ display: none; }}
        }}
        
        @media (max-width: 768px) {{
            .brochure-header {{ padding: 40px 20px; }}
            .brochure-header h1 {{ font-size: 2rem; }}
            .brochure-content {{ padding: 30px 20px; }}
            .brochure-content h2 {{ font-size: 1.8rem; }}
        }}
        
        html {{ scroll-behavior: smooth; }}
    </style>
</head>
<body>
    <div class="page-wrapper">
        <header class="brochure-header">
            {logo_html}
            <h1>{company_name}</h1>
            <p class="brochure-subtitle">Professional Company Brochure</p>
            <div class="header-badge">📄 Marketing Material</div>
            {f'<div class="header-badge">🌐 {company_url}</div>' if company_url else ''}
        </header>
        
        <main class="brochure-content">
            {html_content}
        </main>
        
        <footer class="brochure-footer">
            <h2>Ready to Connect?</h2>
            <p style="font-size: 1.2rem; color: var(--gray); margin: 20px 0;">
                Get in touch with us today to discover how we can help you achieve your goals.
            </p>
            {f'<a href="{company_url}" class="cta-button">🌐 Visit Website</a>' if company_url else ''}
            <a href="javascript:window.print()" class="cta-button">📄 Print Brochure</a>
            
            <p style="margin-top: 40px; color: var(--gray); font-size: 0.9rem;">
                Generated by AI Brochure Generator | © {company_name}
            </p>
        </footer>
    </div>
</body>
</html>"""