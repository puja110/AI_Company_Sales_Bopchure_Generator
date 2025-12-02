from flask import Flask, render_template, request, jsonify, Response
from brochure_generator import BrochureGenerator
import markdown
import json
import traceback
import os  # Add this import

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
        # Generate brochure
        print("Generating brochure...")
        brochure_content = generator.create_brochure(company_name, url)
        
        if brochure_content:
            # Convert markdown to HTML
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
                # Send each chunk as a server-sent event
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Send completion signal
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

if __name__ == '__main__':
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Determine if running in production
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