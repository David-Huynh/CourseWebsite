window.onload = function() {
    const testModal = document.getElementById("testModal");
    const testModalButton = document.getElementById("testButton");
    const testClose = document.getElementsByClassName("close")[1];
    
    const assignmentModal = document.getElementById("assignmentModal");
    const assignmentModalButton = document.getElementById("assignmentButton");
    const assignmentModalClose = document.getElementsByClassName("close")[0];

    testModalButton.onclick = function(event) {
        testModal.style.display = "block";
    }

    testClose.onclick = function(event) {
        testModal.style.display = "none";
    }
    assignmentModalButton.onclick = function(event) {
        assignmentModal.style.display = "block";
    }
    assignmentModalClose.onclick = function(event) {
        assignmentModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == testModal) {
            testModal.style.display = "none";
        }
        if (event.target == assignmentModal){
            assignmentModal.style.display = "none";
        }
    }
}

