$(".login_twitter").on('click', function(ev){
    ev.preventDefault();
    OAuth.popup('twitter', function(error, result) {
      	if (error) {
      		alert(error);
		}
		else {
			oauth_token = result.oauth_token
			oauth_token_secret = result.oauth_token_secret
			window.location.href = "./login?oauth_token="+oauth_token+"&oauth_token_secret="+oauth_token_secret;
		}
    });
  });