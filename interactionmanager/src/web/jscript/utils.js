// function to shuffle a list of objects
function shuffle(a) {
    var j,x,i;
    for (i = a.length; i; i-=1) {
        j = Math.floor(Math.random() * i);
        x = a[i-1];
        a[i-1] = a[j];
        a[j] = x;
    }
}

// function to sum all entries of an array.
function sum_array(a) {
    return a.reduce(function (pv, cv) { return pv + cv; },0);
}

// some time.sleep function
function sleepFor(sleepDuration) {
    var now = new Date().getTime();
    while(new Date().getTime() < now + sleepDuration) {/* do nothing*/}
}