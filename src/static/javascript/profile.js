window.onload = function() {
    const acc_modal = document.getElementById("account_modal");
    const acc_btn = document.getElementById("editA");
    const span1 = document.getElementsByClassName("close")[0];

    const prof_modal = document.getElementById("profile_modal");
    const prof_btn = document.getElementById("editB");
    const span2 = document.getElementsByClassName("close")[1];

    acc_btn.onclick = function(event) {
        acc_modal.style.display = "block";
        console.log('Hello now')

    }

    span1.onclick = function(event) {
        acc_modal.style.display = "none";
    }
   
    prof_btn.onclick = function(event) {
        prof_modal.style.display = "block";
        console.log('Hello now')

    }

    span2.onclick = function(event) {
        prof_modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == prof_modal) {
            prof_modal.style.display = "none";
        } else if (event.target == acc_modal) {
            acc_modal.style.display = "none";
        }
    }
}