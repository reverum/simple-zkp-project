from flask import Flask, render_template_string, request, send_file
import json
import subprocess
import os

def normalize_birth_year(dob_str):
    try:
        parts = dob_str.strip().split('-')
        return int(parts[0]) if len(parts[0]) == 4 else int(parts[2])
    except:
        raise ValueError("Format tanggal lahir tidak dikenali.")

app = Flask(__name__)

ZKEY_PATH = "build/proof_circuit.zkey"
JS_WITNESS_GENERATOR = "build/proof_circuit_js/generate_witness.js" 
WASM_PATH = "build/proof_circuit_js/proof_circuit.wasm" 

@app.route('/')
def index_penduduk():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head><title>Data Penduduk (Prover)</title></head>
    <body style="font-family: Arial; background-color: #C7DFED; padding: 20px;">
        <div style="background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: auto;">
            <h2>National ID Proof Generator</h2>
            <p>Upload <b>KTP.json</b>. Bukti akan dibuat untuk <b>NIK dan Tahun Lahir</b> saja.</p>
            <form method="POST" enctype="multipart/form-data" action="/generate-proof">
                <input type="file" name="ktp_file" accept=".json" required><br><br>
                <button type="submit" style="background: #00bfff; color: white; padding: 10px; border: none; cursor: pointer;">GENERATE PROOF</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/generate-proof', methods=['POST'])
def generate_proof():
    if 'ktp_file' not in request.files: return "File missing", 400
    file = request.files['ktp_file']
    try:
        ktp_data = json.loads(file.read().decode('utf-8'))
        nik = ktp_data['nik']
        birth_year = normalize_birth_year(ktp_data['tanggal_lahir'])

        input_data = {
            "private_nik": str(nik),
            "private_birth_year": str(birth_year),
            "public_nik": str(nik),
            "public_birth_year": str(birth_year)
        }
        
        with open('build/input.json', 'w') as f: json.dump(input_data, f)

        subprocess.run(['node', JS_WITNESS_GENERATOR, WASM_PATH, 'build/input.json', 'build/witness.wtns'], check=True)
        subprocess.run(['snarkjs', 'groth16', 'prove', ZKEY_PATH, 'build/witness.wtns', 'build/proof.json', 'build/public.json'], check=True)

        with open('build/proof.json', 'r') as f_proof: proof = json.load(f_proof)
        with open('build/public.json', 'r') as f_public: public = json.load(f_public)
        
        proof_package = {
            "proof": proof,
            "public_signals": public,
            "description": "ZK Proof for NIK & Birth Year consistency"
        }
        
        output_file = "age_verification_proof.json"
        with open(output_file, 'w') as f: json.dump(proof_package, f, indent=2)
        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
