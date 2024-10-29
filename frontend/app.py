"""Flask app for podcast generation madlib form."""

from flask import Flask, render_template, request, jsonify
import yaml
import os
import json

app = Flask(__name__)

def load_madlib_form():
    """Load madlib form configuration."""
    form_path = os.path.join('..', 'data', 'prompts', 'madlib_form.yaml')
    with open(form_path, 'r') as f:
        return yaml.safe_load(f)

def load_madlib_template():
    """Load madlib template."""
    template_path = os.path.join('..', 'data', 'prompts', 'madlib_template.txt')
    with open(template_path, 'r') as f:
        return f.read()

@app.route('/')
def index():
    """Render the madlib form."""
    form_config = load_madlib_form()
    return render_template('index.html', config=form_config)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate podcast content from form data."""
    form_data = request.json
    template = load_madlib_template()
    
    # Format template with form data
    try:
        # Save form data
        output_path = os.path.join('..', 'data', 'prompts', 'custom_prompt.yaml')
        with open(output_path, 'w') as f:
            yaml.dump(form_data, f)
        
        # Generate formatted content
        formatted_content = template.format(**form_data)
        
        return jsonify({
            'success': True,
            'content': formatted_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
