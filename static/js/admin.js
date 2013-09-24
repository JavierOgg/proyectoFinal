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

	if (id=='submit_ir_a_entrenamiento'){
		$("#form_entrenamiento").submit();
	}

	//self.addClass("btn-warning");
	switch(id){
		case 'obtener_tweets':
			termino_busqueda = $("#termino_busqueda_tweets").val();
			tipoTweets = $("#contactForm input:checked").val();
			datos.termino = termino_busqueda;
			datos.tipoTweets = tipoTweets;
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

	$('.box-btn').not(this).css('opacity','0.2');
	$('fieldset').css('opacity','0.2');
	$.ajax({
		type: tipo,
		url: './admin/utilidades/'+id,
		data: datos
	}).done(function( data ) {
		$('.box-btn').css('opacity','1');
		$('fieldset').css('opacity','1');
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