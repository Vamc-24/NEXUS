from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime 
import uuid

# Add project root to path so we can import ai_module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.storage import get_storage
from ai_module.pipeline import run_pipeline

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

storage = get_storage()

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Extract extended metadata
    feedback_data = {
        'text': data.get('text'),
        'category': data.get('category', 'general'),
        'role': data.get('role', 'Anonymous'),
        'is_verified': data.get('is_verified', False),
        'user_id': data.get('user_id', 'Anonymous'),
        'user_name': data.get('user_name', 'Anonymous'),
        'timestamp': datetime.now().isoformat()
    }
    
    record = storage.add_feedback(feedback_data)
    
    return jsonify({'status': 'success', 'id': record['id']}), 201

@app.route('/api/process', methods=['POST'])
def trigger_processing():
    """
    Manually trigger the AI pipeline.
    In production, this would be a Cloud Function triggered by Firestore events.
    """
    try:
        result = run_pipeline(storage)
        return jsonify({'status': 'success', 'result': result}), 200
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    results = storage.get_latest_results()
    return jsonify(results)

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    from fpdf import FPDF
    data = request.json
    results = data.get('results', [])
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Nexus: Strategic Solution Report", ln=1, align='C')
    pdf.ln(10)
    
    def safe_text(text):
        if text is None:
            return ""
        s = str(text)
        # Replace Rupee symbol and other potential non-latin-1 chars
        s = s.replace('₹', 'Rs. ').replace('\u20b9', 'Rs. ')
        # Encode to latin-1, replacing errors to avoid crash
        return s.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=safe_text("Nexus: Strategic Solution Report"), ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=safe_text(f"Generated on: {datetime.now().strftime('%d %B %Y, %H:%M')}"), ln=1, align='C')
    pdf.ln(10)
    
    for idx, cluster in enumerate(results.get('clusters', [])):
        # Cluster Header
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, txt=safe_text(f"#{idx+1} {cluster.get('theme')}"), ln=1, fill=True)
        
        pdf.set_font("Arial", 'I', 11)
        pdf.multi_cell(0, 8, txt=safe_text(f"Issue: {cluster.get('problem_statement')}"))
        pdf.ln(2)
        
        # Solutions
        for sol in cluster.get('solutions', []):
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(41, 151, 255) # Blue accent
            pdf.cell(0, 10, txt=safe_text(f"Strategy: {sol.get('solution_title', 'Proposed Solution')}"), ln=1)
            pdf.set_text_color(0, 0, 0) # Reset color
            
            # Cost & Resources
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(40, 8, txt="Estimated Cost:", border=0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, txt=safe_text(f"Rs. {sol.get('total_estimated_cost', 'N/A')}"), ln=1)
            
            res = sol.get('resources', {})
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(40, 8, txt="Investment:", border=0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, txt=safe_text(res.get('Investment', '-')), ln=1)

            # Steps
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, txt="Execution Plan:", ln=1)
            pdf.set_font("Arial", '', 10)
            for step in sol.get('steps', []):
                pdf.cell(10, 8, txt="-")
                pdf.multi_cell(0, 8, txt=safe_text(step))
            
            pdf.ln(5)
        pdf.ln(5)

    filename = f"report_{uuid.uuid4()}.pdf"
    
    # Ensure static directory exists
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend')
    filepath = os.path.join(static_dir, filename)
    
    try:
        pdf.output(filepath)
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'url': f'/{filename}'})

@app.route('/api/export/docx', methods=['POST'])
def export_docx():
    from docx import Document
    data = request.json
    results = data.get('results', [])
    
    document = Document()
    document.add_heading('Nexus: Student Feedback Analysis Report', 0)
    document.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    for cluster in results.get('clusters', []):
        document.add_heading(f"Theme: {cluster.get('theme')}", level=1)
        document.add_paragraph(f"Problem: {cluster.get('problem_statement')}")
        
        for idx, sol in enumerate(cluster.get('solutions', [])):
            document.add_heading(f"Solution {idx+1}: {sol.get('solution_title', 'Solution')}", level=2)
            document.add_paragraph(f"Cost: Rs. {sol.get('total_estimated_cost')}")
            
            res = sol.get('resources', {})
            p = document.add_paragraph()
            p.add_run("Investment: ").bold = True
            p.add_run(f"{res.get('Investment')}\n")
            p.add_run("Labor: ").bold = True
            p.add_run(f"{res.get('Labor')}\n")

            document.add_heading("Steps:", level=3)
            for step in sol.get('steps', []):
                document.add_paragraph(step, style='List Bullet')

    filename = f"report_{uuid.uuid4()}.docx"
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend')
    filepath = os.path.join(static_dir, filename)
    
    try:
        document.save(filepath)
    except Exception as e:
        print(f"Error saving DOCX: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'url': f'/{filename}'})

@app.route('/api/institute/register', methods=['POST'])
def register_institute():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Institute Name Required'}), 400
        
    try:
        institute_id = storage.register_institute(data)
        return jsonify({'status': 'success', 'id': institute_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/institute/verify', methods=['POST'])
def verify_institute():
    data = request.json
    institute_id = data.get('id')
    
    if not institute_id:
        return jsonify({'valid': False}), 400
        
    inst_name = storage.verify_institute(institute_id)
    if inst_name:
        return jsonify({'valid': True, 'name': inst_name}), 200
    return jsonify({'valid': False}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
