$(".js-ajax").on('click',function(){

	var self = $(this),
		id = this.id,
		tipo = "GET",
		datos = {},
		mostrarToastr = true,
		url,
		categorias,
		respuesta;

	if (id=='submit_ir_a_entrenamiento'){
		$("#form_entrenamiento").submit();
	}

	//self.addClass("btn-warning");
	switch(id){
		case 'obtener_tweets':
			datos.termino = $("#termino_busqueda_tweets").val();
			datos.tipoTweets = $("#contactForm input:checked").val();
			tipo = "POST";
			break;
		case 'clasificar_tweets_entrenamiento':
			datos.categorias = $("#categorias").val();
			datos.termino = $("#termino").val()
			tipo = "POST";
			mostrarToastr = false;
			$("#busquedas_realizadas").append("<li>"+datos.termino+"</li>");
			break;
		case 'reentrenar_clasificador':
			tipo = "POST";
			break;
		case 'reentrenar_clasificador_archivo':
			tipo = "POST";
			datos.archivo = $("#archivo_csv").val();
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
				boton = '<div class="box-btn"> \
			              	<a href="#" class="js-ajax" id="guardar_tweets_clasificados"> \
			              		<div class="box-btn-txt">Guardar tweets categorizados</div> \
              				</a> \
          				</div>';
				respuesta.append(boton)
				$("#guardar_tweets_clasificados").on('click', function(){
					guardar_tweets_clasificados();
				});
				$("#respuesta tr")
					.focusin(function() {
				  		$( this ).css("background-color", "#bfc66c" );
					})
					.focusout(function(){
						$( this ).css("background-color", "white" );
					});
				$("#respuesta .radioButton:first").focus();
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
		clasificacion = $(this).find(".radioButton:checked").val();
		if (clasificacion=="descartar")
			return
		elem = {};
		elem.tweet = $(this).find(".tweet").text();
		elem.id = $(this).find('.tweetId').val();
		elem.clasificacion
		datos.push(elem);
	});

	$.ajax({
		type: 'POST',
		url: './admin/utilidades/guardar_tweets_entrenamiento',
		data: {
				'entrenamiento': JSON.stringify(datos),
				'archivo': $("#archivo").val()
			}
	}).done(function( data ) {
		toastr.success(data);
	});

}
