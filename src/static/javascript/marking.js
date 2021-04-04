window.onload = function() {
    var saveText = document.getElementById("saveText")
    //Sends post request promise to server
    async function postData(url = '', data = {}) {
        const response = await fetch(url, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          redirect: 'follow',
          body: JSON.stringify(data) 
        });
        return response.json(); 
    }
    //Adds data on grade change for each grade cell
    document.querySelectorAll("input").forEach((element)=>{
        element.onchange = () => {
            saveText.innerHTML="Saving"
            console.log(element.value)
            if (!isNaN(Number(element.value))){
                postData(window.location.protocol+"//"+window.location.host+"/submitMarks", 
                {
                    type:element.id.split("///")[0],
                    assessment_no:element.id.split("///")[1],
                    student_no:element.id.split("///")[2],
                    grade:Number(element.value)
                }).then(data=>{
                    saveText.innerHTML="Auto Saved"
                    console.log(data)
                })
            }
        }
    })
}