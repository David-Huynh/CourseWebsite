window.onload = function() {
    const lectureModal = document.getElementById("lectureModal");
    const lectureModalButton = document.getElementById("lecture");
    const lectureClose = document.getElementsByClassName("close")[1];
    
    const pdfModal = document.getElementById("coursePdf");
    const pdfModalButton = document.getElementById("coursePdfButton");
    const pdfModalClose = document.getElementsByClassName("close")[0];

    lectureModalButton.onclick = function(event) {
        lectureModal.style.display = "block";
    }

    lectureClose.onclick = function(event) {
        lectureModal.style.display = "none";
    }
    pdfModalButton.onclick = function(event) {
        pdfModal.style.display = "block";
    }
    pdfModalClose.onclick = function(event) {
        pdfModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == lectureModal) {
            lectureModal.style.display = "none";
        }
        if (event.target == pdfModal){
            pdfModal.style.display = "none";
        }
    }
}

