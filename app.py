from flask import Flask, render_template, request, jsonify, Response, send_file
from brochure_generator import BrochureGenerator
import markdown
import json
import traceback
import os
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

generator = None

def init_generator():
    global generator
    try:
        if generator is None:
            print("Initializing BrochureGenerator...")
            generator = BrochureGenerator()
            print("BrochureGenerator initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing generator: {e}")
        traceback.print_exc()
        return False

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate brochure (non-streaming)"""
    print("=== Generate request received ===")
    
    if not init_generator():
        return jsonify({
            'success': False,
            'error': 'Failed to initialize AI generator. Please check your API key in .env file.'
        }), 500
    
    data = request.json
    company_name = data.get('company_name', '').strip()
    url = data.get('url', '').strip()
    
    print(f"Company: {company_name}, URL: {url}")
    
    if not company_name or not url:
        return jsonify({
            'success': False,
            'error': 'Company name and URL are required'
        }), 400
    
    try:
        print("Generating brochure...")
        brochure_content = generator.create_brochure(company_name, url)
        
        if brochure_content:
            print("Converting markdown to HTML...")
            html_content = markdown.markdown(
                brochure_content,
                extensions=['extra', 'codehilite', 'nl2br']
            )
            
            print("Brochure generated successfully!")
            return jsonify({
                'success': True,
                'markdown': brochure_content,
                'html': html_content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate brochure content'
            }), 500
            
    except Exception as e:
        print(f"Error in generate: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

@app.route('/generate-stream', methods=['POST'])
def generate_stream():
    """Generate brochure with streaming"""
    print("=== Stream generate request received ===")
    
    if not init_generator():
        return Response(
            json.dumps({
                'error': 'Failed to initialize AI generator. Please check your API key in .env file.'
            }),
            mimetype='application/json',
            status=500
        )
    
    data = request.json
    company_name = data.get('company_name', '').strip()
    url = data.get('url', '').strip()
    
    print(f"Company: {company_name}, URL: {url}")
    
    if not company_name or not url:
        return Response(
            json.dumps({'error': 'Company name and URL are required'}),
            mimetype='application/json',
            status=400
        )
    
    def generate_stream_response():
        """Stream the brochure generation"""
        try:
            print("Starting stream generation...")
            for chunk in generator.stream_brochure(company_name, url):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            print("Stream generation complete")
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            print(f"Error in stream: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        generate_stream_response(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/generate-interactive-html', methods=['POST'])
def generate_interactive_html():
    """Generate interactive HTML brochure with all enhancements"""
    print("=== Interactive HTML generation request ===")
    
    try:
        data = request.json
        markdown_content = data.get('markdown', '')
        company_name = data.get('company_name', 'Company')
        company_url = data.get('company_url', '')
        animation_style = data.get('animation_style', 'fade')
        template_style = data.get('template_style', 'professional')
        
        if not markdown_content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        if not init_generator():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize generator'
            }), 500
        
        html_content = generator.generate_interactive_html(
            markdown_content,
            company_name,
            company_url,
            animation_style,
            template_style
        )
        
        return jsonify({
            'success': True,
            'html': html_content
        })
        
    except Exception as e:
        print(f"Error generating interactive HTML: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF brochure"""
    print("=== PDF generation request ===")
    
    try:
        data = request.json
        markdown_content = data.get('markdown', '')
        company_name = data.get('company_name', 'Company')
        company_url = data.get('company_url', '')
        
        if not markdown_content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        if not init_generator():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize generator'
            }), 500
        
        pdf_bytes = generator.generate_pdf_brochure(
            markdown_content,
            company_name,
            company_url
        )
        
        if pdf_bytes:
            safe_filename = company_name.replace(' ', '_').replace('/', '_')
            filename = f"{safe_filename}_brochure.pdf"
            
            return send_file(
                BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate PDF'
            }), 500
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/extract-assets', methods=['POST'])
def extract_assets():
    """Extract company assets (logo, images, colors, social media)"""
    print("=== Asset extraction request ===")
    
    try:
        data = request.json
        company_url = data.get('url', '').strip()
        
        if not company_url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        if not init_generator():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize generator'
            }), 500
        
        logo = generator.extract_company_logo(company_url)
        images = generator.extract_company_images(company_url, max_images=6)
        colors = generator.extract_brand_colors(company_url, logo)
        social_media = generator.extract_social_media(company_url)
        
        return jsonify({
            'success': True,
            'logo': logo,
            'images': images,
            'colors': colors,
            'social_media': social_media
        })
        
    except Exception as e:
        print(f"Error extracting assets: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    print("Starting Flask application...")
    print(f"Environment: {'Production' if is_production else 'Development'}")
    print(f"Server will run on port: {port}")
    
    app.run(
        debug=not is_production,
        host='0.0.0.0',
        port=port,
        threaded=True
    )