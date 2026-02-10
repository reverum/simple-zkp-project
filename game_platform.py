from flask import Flask, render_template_string, request, redirect, url_for, flash
import json
import subprocess

def normalize_birth_year(dob_str):
    try:
        return int(dob_str.strip().split('-')[2])
    except Exception:
        raise ValueError("Format tanggal lahir harus DD-MM-YYYY.")

app = Flask(__name__)
app.secret_key = 'isi_apa_aja_terserah' 
VKEY_PATH = "build/verification_key.json"
CURRENT_YEAR = 2025
GAME_MIN_AGE = 18

@app.route('/')
def index_game():
    html_content = f'''
    <!DOCTYPE html>
    <html lang="id">
    <head><title>Game Platform (Verifier)</title></head>
    <body style="font-family: Arial; background-color: #e6ffe6; padding: 20px;">
        <div style="background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: auto;">
            <h2>Verifikasi Akses Game (ZKP)</h2>
            <p>Input NIK & Tanggal Lahir untuk memverifikasi usia (Min: {GAME_MIN_AGE} tahun).</p>
            <form method="POST" enctype="multipart/form-data" action="/verify-proof">                
                <label>NIK:</label><br>
                <input type="text" name="nik" placeholder="3333330707970007" required style="width:100%;"><br><br>
                <label>Tanggal Lahir (DD-MM-YYYY):</label><br>
                <input type="text" name="dob" placeholder="07-07-1997" required style="width:100%;"><br><br>
                <label>Upload ZK Proof File:</label><br>
                <input type="file" name="proof_file" accept=".json" required><br><br>
                <button type="submit" style="background: #4CAF50; color: white; padding: 10px; border: none; cursor: pointer;">VERIFY PROOF</button>
            </form>
            <hr>
            {{% with messages = get_flashed_messages() %}}
                {{% if messages %}}
                    <p style="color: blue; font-weight: bold;">{{{{ messages[0] }}}}</p>
                {{% endif %}}
            {{% endwith %}}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/verify-proof', methods=['POST'])
def verify_proof():
    if 'proof_file' not in request.files: 
        return redirect(url_for('index_game'))
    
    file = request.files['proof_file']
    
    try:
        proof_package = json.loads(file.read().decode('utf-8'))
        available_signals = proof_package['public_signals'] 

        nik_input = request.form.get('nik')
        dob_input = request.form.get('dob')

        nik = str(nik_input)
        birth_year = str(normalize_birth_year(dob_input))
        
        if len(available_signals) < 2:
            flash("Bukti ZK tidak valid (jumlah sinyal kurang).")
            return redirect(url_for('index_game'))

        is_consistent = (
            available_signals[0] == nik and
            available_signals[1] == birth_year
        )

        if not is_consistent:
            flash("Data input TIDAK COCOK dengan Bukti ZK!")
            return redirect(url_for('index_game'))
        
        with open('build/verify_proof.json', 'w') as f: 
            json.dump(proof_package['proof'], f)
        with open('build/verify_public.json', 'w') as f: 
            json.dump(available_signals, f) 

        result = subprocess.run(
            ['snarkjs', 'groth16', 'verify', VKEY_PATH, 'build/verify_public.json', 'build/verify_proof.json'], 
            capture_output=True, text=True
        )

        if "OK" in result.stdout:
            age_limit_year = CURRENT_YEAR - GAME_MIN_AGE 
            proof_year = int(available_signals[1])
            
            if proof_year <= age_limit_year:
                flash(f"BERHASIL! ✅ Usia cukup ({CURRENT_YEAR - proof_year} thn). Selamat bermain!")
            else:
                flash(f"GAGAL! ❌ Usia belum mencapai {GAME_MIN_AGE} tahun.")
        else:
            flash("KRITIS: Bukti Palsu atau Telah Dimodifikasi! ❌")
            
        return redirect(url_for('index_game'))

    except Exception as e:
        flash(f"Terjadi Kesalahan: {str(e)}")
        return redirect(url_for('index_game'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)