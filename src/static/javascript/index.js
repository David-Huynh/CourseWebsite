$(document).ready(function(){
    $("#dropmenu").change(function () {
        var option = $("#dropmenu option:selected").val();
        console.log(option);
        if(option=="Signin")
        {
            $("#signinButton").show();
            $("#registerForm").hide();
            $("#registerForm input").removeAttr('required');

        }else{
            $("#signinButton").hide();
            $("#registerForm").show();
            $("#registerForm input").attr('required', '');
        }
    });
});
