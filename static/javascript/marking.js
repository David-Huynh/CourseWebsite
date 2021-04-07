window.onload = function() {
    //TODO: Automatically handle broadcast of new student submissions and render it
    var saveText = document.getElementById("saveText")
    var socket = io();
    //Establishes connection to socket on server
    socket.on('connect', function() {
        console.log(socket.id);
    });
    //Handles json data from server
    socket.on('json', (data)=>{
        saveText.innerHTML="Auto Saved"
        console.log(data)
        if (data !== null){
            document.getElementById(data["type"]+"///"+data["assessment_no"]+"///"+data["student_no"]).value=data["grade"]
            document.getElementsByName(data["type"]+"///"+data["assessment_no"]+"///marked").forEach((element)=>{
                element.innerHTML="&check;"
            })
            document.getElementsByName(data["type"]+"///"+data["assessment_no"]+"///regrade").forEach((element)=>{
                element.innerHTML="&#10005;"
            })
        }
    });
    socket.on("disconnect", (reason) => {
        console.log(reason)
    });
    
    //Adds data on grade change for each grade cell
    document.querySelectorAll("input").forEach((element)=>{
        element.onchange = () => {
            saveText.innerHTML="Saving"
            console.log(element.value)
            if (!isNaN(Number(element.value))){
                //Sends updated data to socket
                socket.emit("json", {
                    type:element.id.split("///")[0],
                    assessment_no:element.id.split("///")[1],
                    student_no:element.id.split("///")[2],
                    grade:Number(element.value)
                });
            }
        }
    })
}