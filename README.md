
## DISCLAIMER:

- Project ini dibuat untuk tujuan **edukasi dan demonstrasi konsep** Zero Knowledge Proof (ZKP) sederhana.
- Kode ini bersifat ***eksperimental***
- Kode ini disediakan **"sebagaimana adanya"** (_as-is_). Jika Anda menemukan error, kendala instalasi, atau sirkuit yang tidak mau kompilasi, saya tidak memberikan bantuan teknis atau perbaikan (support)
- Segala risiko yang ditimbulkan karena penggunaan kode ini (contoh: komputer jadi lemot, salah download, dsb) sepenuhnya menjadi tanggung jawab pengguna tanpa jaminan dalam bentuk apa pun
- Project ini dibuat dan dijalankan di Ubuntu Server 24.04. Jika menggunakakn distro atau platform lain, harap disesuaikan sendiri
----------------------------

## Persiapan:
Clone project ini, kemudian masuk ke direktori project.

## Step 1: Install Tools
**Update System & Install Basic Tools:**

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl git build-essential python3-pip nodejs npm
    pip3 install flask

**Install Rust**

    curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
Tekan 1 lalu Enter (default). Setelah itu:

    source $HOME/.cargo/env

**Install Circom (circuit compiler)**

    git clone https://github.com/iden3/circom.git
    cd circom
    cargo build --release
    sudo cp target/release/circom /usr/local/bin/
    cd ..
    rm -rf circom

Cek instalasi dengan mengetik `circom --version`

**Install SnarkJS Library**

    sudo npm install -g snarkjs

**Install CircomLib**
	
	git clone https://github.com/iden3/circomlib.git

## Step 2: Kompilasi
    circom proof_circuit.circom --r1cs --wasm --sym -o build
    snarkjs groth16 setup build/proof_circuit.r1cs build/powersOfTau28_hez_final_12.ptau build/circuit_0000.zkey
    snarkjs zkey contribute build/circuit_0000.zkey build/proof_circuit.zkey --name="MyKTPProject" -v -e="random_text_bebas"
    snarkjs zkey export verificationkey build/proof_circuit.zkey build/verification_key.json

## Step 3: Jalankan Program
**NOTE:** Jalankan kedua perintah ini dengan menggunakan ***dua terminal yang berbeda***. Contoh: menggunakan `tmux`

  Terminal #1:

     python3 data_penduduk.py

  Terminal #2:
 
     python3 game_platform.py

## Step 4: Simulasi Penggunaan
Jika data_penduduk dan game_platform sudah berhasil dijalankan, buka web browser di komputer.

**Generate Proof (Sebagai Bob)**

 1. Buka `http://localhost:5000`
 2. Anda akan melihat halaman "National ID Proof Generator". 
 3. Klik **Choose File** dan pilih `ktp_bob.json` yang disertakan dalam project ini
 4. Klik **GENERATE PROOF**
 5. Sistem akan mendownload file    bernama `age_verification_proof.json`
Simpan file `age_verification_proof.json` ini untuk step selanjutnya.

**Verifikasi**

 1. Buka tab baru ke `http://localhost:5001`    
 2. Anda akan melihat halaman "Integrated Digital Residency & Identity...".   
 3. Isi Form:
			NIK: `3333330707970007` (Sesuai ktp_bob)
			Tanggal Lahir: `07-07-1997` (Sesuai ktp_bob, format DD-MM-YYYY)
			Upload ZK Proof File: Pilih file `age_verification_proof.json` yang sudah didownload di step sebelumnya
 4. Klik **VERIFY PROOF**.

----------------------------
**Built With**
This project leverages the following open-source technologies:
* **[Circom 2.0](https://docs.circom.io/)** - DSL for writing Zero Knowledge circuits.
* **[SnarkJS](https://github.com/iden3/snarkjs)** - zkSNARK implementation in JavaScript/WASM by iden3.
* **[circomlib](https://github.com/iden3/circomlib)** - Standard library for Circom circuits (specifically using `comparators.circom` for age verification logic).
* **[Flask](https://flask.palletsprojects.com/)** - Lightweight WSGI web application framework for Python.

This project is licensed under the GPL-3.0 License
