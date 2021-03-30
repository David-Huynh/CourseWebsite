window.onload = function() {

    var realFileBtn = document.getElementById("real-file");
    var customBtn = document.getElementById("upload-button");
    var customTxt = document.getElementById("upload-text");
    // temporary fix for having two of the same buttons
    var realFileBtn2 = document.getElementById("real-file2");
    var customBtn2 = document.getElementById("upload-button2");
    var customTxt2 = document.getElementById("upload-text2");

    const modal = document.getElementById("myModal");
    const btn = document.getElementById("editB");
    const span = document.getElementsByClassName("close")[0];
    
    customBtn.addEventListener("click", function() {
        realFileBtn.click();
    })

    realFileBtn.addEventListener("change", function() {
        if (realFileBtn.value) {
            customTxt.innerHTML = realFileBtn.value.match(
            /[\/\\]([\w\d\s\.\-\(\)]+)$/
            )[1];
        } else {
            customTxt.innerHTML = "No file chosen, yet.";
        }
    })

    customBtn2.addEventListener("click", function() {
        realFileBtn2.click();
    })

    realFileBtn2.addEventListener("change", function() {
        if (realFileBtn2.value) {
            customTxt2.innerHTML = realFileBtn2.value.match(
            /[\/\\]([\w\d\s\.\-\(\)]+)$/
            )[1];
        } else {
            customTxt2.innerHTML = "No file chosen, yet.";
        }
    })

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

