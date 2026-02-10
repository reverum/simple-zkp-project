pragma circom 2.0.0;
include "circomlib/circuits/comparators.circom";

template IdentityProof() {
    signal input private_nik;
    signal input private_birth_year;

    signal input public_nik;
    signal input public_birth_year;
  
    private_nik === public_nik;
    private_birth_year === public_birth_year;

    signal output out_nik;
    out_nik <== public_nik;

    signal output out_birth_year;
    out_birth_year <== public_birth_year;
}

component main = IdentityProof();