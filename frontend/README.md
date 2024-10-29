# Podcast Generator Frontend

A simple Flask web application for generating podcast content using a madlib-style form.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open in browser:
```
http://localhost:5000
```

## Features

- Dark mode interface
- Real-time preview
- Form validation
- Dropdown selections for consistent content
- Automatic YAML generation
- Template-based content generation

## Structure

- `app.py`: Main Flask application
- `templates/index.html`: Frontend interface
- `requirements.txt`: Python dependencies
- `../data/prompts/madlib_form.yaml`: Form configuration
- `../data/prompts/madlib_template.txt`: Content template
- `../data/prompts/custom_prompt.yaml`: Generated output
