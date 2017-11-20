function statusChangeCallback(response) {
    if (response.status === 'connected') {
        testAPI();
    } else if(response.status == 'not_authorized'){
        document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    } else {
        document.getElementById('status').innerHTML = 'Log in' + 'with Facebook to share streams with your friends and groups.';
    }
}


function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

window.fbAsyncInit = function() {
    FB.init({
        appId      : '1726616160711665',
        cookie     : true,  // enable cookies to allow the server to access
                            // the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.8' // use graph api version 2.8
    });

    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};

(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8&appId=281792408977399";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
        console.log('Successful login for: ' + response.name);
        document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
}