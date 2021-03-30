window.onload = function() {
    var dropmenu = document.getElementById("dropmenu");
    dropmenu.addEventListener("change", () => {
        var option = dropmenu.value;
        if(option=="Signin"){
            document.getElementById("signinButton").style.display="block";
            document.getElementById("registerForm").style.display="none";
            document.getElementById("studentForm").style.display="none";
            document.getElementById("regtypemenu").style.display="none";
            document.getElementById("registerForm").removeAttribute("required");
            document.getElementById("studentForm").removeAttribute("required");
        }else if (option=="Register"){
            document.getElementById("registerForm").style.display="block";
            document.getElementById("regtypemenu").style.display="block";
            document.getElementById("signinButton").style.display="none";
            document.querySelectorAll("#registerForm input").forEach(element => {
                element.setAttribute("required","");
            });
            var regOption = document.getElementById("regtypemenu").value;
            console.log(regOption)
            if (regOption=="Student"){
                document.getElementById("studentForm").style.display="block";
                document.querySelectorAll("#studentForm input").forEach(element => {
                    element.setAttribute("required","");
                });
            }else if (regOption=="Instructor"){
                document.getElementById("studentForm").style.display="none";
                document.querySelectorAll("#studentForm input").forEach(element => {
                    element.removeAttribute("required");
                });
            }
        }
    })
    var regMenu = document.getElementById("regtypemenu");
    regMenu.addEventListener("change", () => {
        var option = regMenu.value;
        console.log(option);
        if(option=="Student"){   
            document.getElementById("studentForm").style.display="block";
            document.querySelectorAll("#studentForm input").forEach(element => {
                element.setAttribute("required","");
            });
        }else if (option=="Instructor"){
            document.getElementById("studentForm").style.display="none";
            document.querySelectorAll("#studentForm input").forEach(element => {
                element.removeAttribute("required");
            });
        }
    }) ;
}
