
template Main() {
    signal input CETRange[2];
 
    signal input CETScore;
 
    signal output out;
 
    component gt1 = GreaterEqThan(10);
    gt1.in[0] <== CETScore;
    gt1.in[1] <== CETRange[0];
    gt1.out === 1;
}
 
template GreaterEqThan(n) {
    signal input in[2];
    signal output out;
 
    component lt = LessThan(n);
 
    lt.in[0] <== in[1];
    lt.in[1] <== in[0]+1;
    lt.out ==> out;
}
 
template LessThan(n) {
    assert(n <= 252);
    signal input in[2];
    signal output out;
 
    component n2b = Num2Bits(n+1);
 
    n2b.in <== in[0]+ (1<<n) - in[1];
 
    out <== 1-n2b.out[n];
}
 
template Num2Bits(n) {
    signal input in;
    signal output out[n];
    var lc1=0;
 
    var e2=1;
    for (var i = 0; i<n; i++) {
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] -1 ) === 0;
        lc1 += out[i] * e2;
        e2 = e2+e2;
    }
 
    lc1 === in;
}
 
component main = Main();
