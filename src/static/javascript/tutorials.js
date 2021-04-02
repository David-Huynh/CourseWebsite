window.onload = function() {
    const pdfModal = document.getElementById("courseTutPdf");
    const pdfModalButton = document.getElementById("coursePdfButton");
    const pdfModalClose = document.getElementsByClassName("close")[0];

    pdfModalButton.onclick = function(event) {
        pdfModal.style.display = "block";
    }
    pdfModalClose.onclick = function(event) {
        pdfModal.style.display = "none";
    }
    window.onclick = function(event) {
        if (event.target == pdfModal){
            pdfModal.style.display = "none";
        }
    }
   
    const tutorialModal = document.getElementById("tutorialModal");
    if (tutorialModal){ 

        const tutorialModalButton = document.getElementById("tutorial");
        const tutorialClose = document.getElementsByClassName("close")[1];
        
        tutorialModalButton.onclick = function(event) {
            tutorialModal.style.display = "block";
        }

        tutorialClose.onclick = function(event) {
            tutorialModal.style.display = "none";
        }
        
        
        window.onclick = function(event) {
            if (event.target == tutorialModal) {
                tutorialModal.style.display = "none";
            }
            
        }
    }
}

