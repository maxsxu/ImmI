$(function () {
    $('#btnSignUp').click(function () {
        console.log("signUp");
        $("form[name='signUp']").submit();
    });

    $('#btnSignIn').click(function () {
        console.log("signIn");
        $("form[name='signIn']").submit();
    });
});
