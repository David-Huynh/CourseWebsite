const navSlide = () => {
    const navBtn = document.getElementById("barBtn")
    const links = document.querySelector(".desktopList")

    navBtn.onclick = function(event) {
        links.classList.toggle("navActive");
        barBtn.classList.toggle("clicked");
    }
}
    
navSlide();