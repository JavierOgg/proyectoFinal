function traer_recomendaciones(recomendacion){
	var self = $(this),
		url,
		respuesta;

	$('.botones-recomendaciones').css('opacity','0.2');

	$.ajax({
		type: "GET",
		url: './interaccion_usuario/'+recomendacion,
	}).done(function( data ) {
		$('.botones-recomendaciones').css('opacity','1');
		respuesta = $('#contenido');
		respuesta.html(data);

		$('.star').rating({
			callback: function(value, link){ 								
				/*var id = $(this).attr('data-id');
				actualizar_puntaje(id, value);*/
			}
		});
	
		$('.aumentar_puntaje').on('click',function(){
			var id = $(this).attr('data-id');
			$.ajax({
				type: "POST",
				url: './interaccion_usuario/aumentar_puntaje',
				data: {'id': id}
			}).done(function( data ) {		
			
			});
		});


		$('.disminuir_puntaje').on('click',function(){
			var id = $(this).attr('data-id');
			$.ajax({
				type: "POST",
				url: './interaccion_usuario/disminuir_puntaje',
				data: {'id': id}
			}).done(function( data ) {		
			
			});
		});

	});
}

$(".botones-recomendaciones").on('click',function(){

	traer_recomendaciones(this.id)
	
});



/*function actualizar_puntaje(id, valor){	
	$.ajax({
		type: "POST",
		url: './interaccion_usuario/actualizar_puntaje',
		data: {'id': id, 'valor': valor}
	}).done(function( data ) {		
	
	});
}*/


traer_recomendaciones('peliculas');