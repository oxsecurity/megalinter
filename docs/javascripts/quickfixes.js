(window.onload = function () {
    // Hide h1 containing Home (to have a nicer home page)
    var h1s = document.querySelectorAll("h1");
    for (var i = 0; i < h1s.length; i++) {
        if (h1s[i].innerText === 'Home') {
            h1s[i].style.display = 'none';
        }
    }
})
