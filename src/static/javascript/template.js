window.onload = function() {
    const navBtn = document.getElementById("barBtn")
    const links = document.querySelector(".desktopList")

    navBtn.onclick = function(event) {
        console.log(event)
        links.classList.toggle("navActive")
    }
}