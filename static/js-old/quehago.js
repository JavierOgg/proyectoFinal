$(".js-ajax").on('click',function(){
	var self = $(this),
		id = this.id,
		tipo = "GET",
		datos = {},
		mostrarToastr = true,
		url,
		categorias,
		termino_busqueda,
		respuesta;

	self.addClass("btn-warning");
	switch(id){
		case 'obtener_tweets':
			termino_busqueda = $("#termino_busqueda_tweets").val();
			datos.termino = termino_busqueda;
			tipo = "POST";
			break;
		case 'clasificar_tweets_entrenamiento':
			categorias = $("#categorias").val();
			datos.categorias = categorias;
			tipo = "POST";
			mostrarToastr = false;
			break;
		case 'mostrar_tweets':
		case 'mostrar_tweets_clasificados':
		case 'mostrar_nes':
		case 'mostrar_sugerencias':
			mostrarToastr = false;
			break;
	}

	$.ajax({
		type: tipo,
		url: './utilidades/'+id,
		data: datos
	}).done(function( data ) {
		if (mostrarToastr){
			toastr.success(data);
		}
		else{
			respuesta = $('#respuesta');
			respuesta.html(data);
			if (id=='clasificar_tweets_entrenamiento') {
				respuesta.append('<button id="guardar_tweets_clasificados">Guardar tweets categorizados</button>', '<hr>');
				$("#guardar_tweets_clasificados").on('click', function(){
					guardar_tweets_clasificados();
				});
			}
		}
		self.removeClass("btn-warning").addClass("btn-success");
	});
});

function guardar_tweets_clasificados(){
	var datos = [],
		tweets,
		clasificacion,
		elem;
		
	$("#tabla_clasificacion tbody tr").each(function() {
		elem = {};
		elem.tweet = $(this).find(".tweet").text();
		elem.clasificacion = $(this).find(".radioButton:checked").val();
		datos.push(elem);
	});
	
	$.ajax({
		type: 'POST',
		url: './utilidades/guardar_tweets_entrenamiento',
		data: { 
				'entrenamiento': JSON.stringify(datos), 
				'archivo': $("#archivo").val()
			}
	}).done(function( data ) {
		toastr.success(data);
	});	

}



$("#login_twitter").on('click', function(ev){
    ev.preventDefault();
    OAuth.popup('twitter', function(error, result) {
      	if (error) {
      		alert(error);
		}
		else {
			oauth_token = result.oauth_token
			oauth_token_secret = result.oauth_token_secret
			window.location.href = "./login?oauth_token="+oauth_token+"&oauth_token_secret="+oauth_token_secret;
			/*oauthProvider = success.provider
			$('#success-text').show().find('span').html(oauthProvider)*/
		}
	      //handle error with error
	      //use result.access_token in your API request
    });  
  });