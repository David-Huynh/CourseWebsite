window.onload = function() {

    const modal = document.getElementById("myModal");
    const btn = document.getElementById("editB");
    const span = document.getElementsByClassName("close")[0];

    btn.onclick = function(event) {
        modal.style.display = "block";
    }

    span.onclick = function(event) {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}