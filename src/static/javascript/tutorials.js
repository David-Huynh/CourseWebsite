window.onload = function() {
    const lectureModal = document.getElementById("tutorialModal");
    const lectureModalButton = document.getElementById("tutorial");
    const lectureClose = document.getElementsByClassName("close")[1];
    
    const pdfModal = document.getElementById("courseTutPdf");
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

