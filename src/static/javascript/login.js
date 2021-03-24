$(document).ready(function(){
    $("#dropmenu").change(function () {
        var option = $("#dropmenu option:selected").val();
        console.log(option);
        if(option=="Signin")
        {
            $("#signinButton").show();
            $("#registerForm").hide();
            $("#studentForm").hide();
            $("#regtypemenu").hide();
            $("#studentForm input").removeAttr('required');
            $("#registerForm input").removeAttr('required');
            

        }else if (option=="Register"){
            $("#signinButton").hide();
            $("#regtypemenu").show();
            $("#registerForm").show();
            $("#registerForm input").attr('required', '');
            //Checks whether student is selected or instructor is selected to show the correct form
            if ($("#regtypemenu option:selected").val()=="Student"){
                $("#studentForm").show();
                $("#studentForm input").attr('required', '');
            }else if ($("#regtypemenu option:selected").val()=="Instructor"){
                $("#studentForm").hide();
                $("#studentForm input").removeAttr('required');
            }
        }
    });
    $("#regtypemenu").change(function () {
        var option = $("#regtypemenu option:selected").val();
        console.log(option);
        if(option=="Student")
        {   
            $("#studentForm").show();
            $("#studentForm input").attr('required', '');
        }else if (option=="Instructor"){
            $("#studentForm").hide();
            $("#studentForm input").removeAttr('required');
        }
    });
});
