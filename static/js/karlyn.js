var page;
var topH;

// cta button rollovers

var boxsp = .3;

$('#btn-help').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#374246', 'borderColor':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:1});
});

$('#btn-help').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#fdc415', 'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:0});
});

$('#footer-btn-email').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#374246', 'borderColor':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:1});
});

$('#footer-btn-email').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#bfc66c', 'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:0});
});

$('#btn-about, #btn-clients, [id^="exp-"] .box-btn').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#374246', 'borderColor':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#fdc415'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:1});
});

$('#btn-about, #btn-clients, [id^="exp-"] .box-btn').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#fdc415', 'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:0});
});




// social links in header

$('#social-links').children('a').mouseover(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:1});
})
$('#social-links').children('a').mouseout(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:0});
})



// box icons rollover

$('.home-box').mouseover(function(){
	TweenMax.to($(this).children('.home-box-img').children('img'),.5,{scaleX:1.2, scaleY:1.2, ease:Expo.easeOut});
});

$('.home-box').mouseleave(function(){
	TweenMax.to($(this).children('.home-box-img').children('img'),.5,{scaleX:1, scaleY:1, ease:Expo.easeOut});
});

$('.home-box').click(function(){
	goID = $(this).attr('id').split('box-')[1];
	location.href = 'expertise.php?p='+goID;
});

$('.home-client-box').click(function(){
	location.href = 'clients.php';
});




// About Page - box icons rollover

$('.bio-photo').mouseover(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:1});
});

$('.bio-photo').mouseout(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:0});
});

$('.bio-box').children('footer').children('a').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#374246', 'borderColor':'#fdc415'});
	TweenMax.to($(this).children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:1});
});

$('.bio-box').children('footer').children('a').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#fdc415', 'borderColor':'#374246'});
	TweenMax.to($(this).children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:0});
});



// Clients Page - boxes rollover

$('.client-box').mouseover(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:1});
});

$('.client-box').mouseout(function(){
	TweenMax.to($(this).children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('.hide'),boxsp,{alpha:0});
});

$('.client-box').click(function(){
	if($(this).attr('data-type') != 'lightbox'){
		window.open($(this).attr('data-url'));
	}
});




// Fearless page - arrows rollover

$('#event-prev, #event-next').mouseover(function(){
	TweenMax.to($(this).children('p'),boxsp,{'color':'#fdc415','backgroundColor':'#374246'});
	TweenMax.to($(this).children('.event-arrow-box').children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('.event-arrow-box').children('.hide'),boxsp,{alpha:1});
});

$('#event-prev, #event-next').mouseout(function(){
	TweenMax.to($(this).children('p'),boxsp,{'color':'#fff','backgroundColor':'#907d73'});
	TweenMax.to($(this).children('.event-arrow-box').children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('.event-arrow-box').children('.hide'),boxsp,{alpha:0});
});

$('#event-prev').click(function(){goSlidePrev();})
$('#event-next').click(function(){goSlideNext();})

// event photo slideshow

var slideTotal = 8;
var slideNum = 1;

$('#slide-photo1').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
$('#slide-photo2').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
TweenMax.set('#slide-photo2', {left:920});

function goSlideNext(){
	slideNum++;
	if(slideNum>slideTotal){
		slideNum = 1;
	}
	
	TweenMax.set('#slide-photo2', {left:920});
	$('#slide-photo2').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
	TweenMax.to('#slide-photo1', .75, {left:-920, ease:Expo.easeInOut});
	TweenMax.to('#slide-photo2', .75, {left:0, ease:Expo.easeInOut, onComplete:function(){
	    $('#slide-photo1').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
	    TweenMax.set('#slide-photo1', {left:0});
	    TweenMax.set('#slide-photo2', {left:920});
	}});
}
function goSlidePrev(){
	slideNum--;
	if(slideNum==0){
		slideNum = slideTotal;
	}
	
	TweenMax.set('#slide-photo2', {left:-920});
	$('#slide-photo2').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
	TweenMax.to('#slide-photo1', .75, {left:920, ease:Expo.easeInOut});
	TweenMax.to('#slide-photo2', .75, {left:0, ease:Expo.easeInOut, onComplete:function(){
	    $('#slide-photo1').children('img').attr('src','images/events/slideshow/photo'+slideNum+'.jpg');
	    TweenMax.set('#slide-photo1', {left:0});
	    TweenMax.set('#slide-photo2', {left:-920});
	}});
}




// Contact page - form actions

$('#form-btn').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#374246', 'borderColor':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#bfc66c'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:0});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:1});
});

$('#form-btn').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#bfc66c', 'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-btn-txt'),boxsp,{'color':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon'),boxsp,{'borderColor':'#374246'});
	TweenMax.to($(this).children('a').children('.box-icon').children('.show'),boxsp,{alpha:1});
	TweenMax.to($(this).children('a').children('.box-icon').children('.hide'),boxsp,{alpha:0});
});

$('#form-btn').children('a').click(function(){
	$('#contactForm').submit();
	return false;
});

// form submission

$('#contactForm').submit(function (){
	validateForm();	
	return false;
});

var sending = false;

function validateForm(){
	var vNum = 0;
	$('[data-rel="req"]').each(function(){
		if($(this).val() == ""){
			vNum++;
			alert("Please fill in all fields.");
			return false; 
		}
	});
	if(vNum==0){
		sendForm();
	}
}

function sendForm(){
	sending = true;
	var name = $('#data-name').val();
	var company = $('#data-company').val();
	var website = $('#data-website').val();
	var email = $('#data-email').val();
	var phone = $('#data-phone').val();
		
	$('#thanks').hide();
	TweenMax.to($('[alt="plane2"]'), .3, {opacity:0});
	TweenMax.to($('#sending'), .5, {delay:.2, opacity:1, 'display':'block'});
	cogspinner = setInterval(spinCog, 30);
	TweenMax.to($('fieldset'), .5, {opacity:.3});
		
	$.ajax({
		url: 'scripts/form.php',
		type: 'POST',
		data: 'name=' + name + '&company=' + company + '&website=' + website + '&email=' + email + '&phone=' + phone,
		
		success: function(result){	
			TweenMax.to($('#sending'), .5, {delay:1.2, opacity:0, 'display':'none', onComplete:function(){					
			    TweenMax.to($('fieldset'), .5, {opacity:1});
				TweenMax.to($('[alt="plane2"]'), .5, {opacity:1});
				TweenMax.to($('#thanks'), .5, {opacity:1, 'display':'block'});
				clearInterval(cogspinner);
			    
			    $('[data-rel="req"]').each(function(){
			    	$(this).val('');
			    });
			    	
			    sending = false;	
			}});				
		}
	});
		
	return false;
}

function spinCog(){
	TweenMax.set($('#sending').children('img'), {rotation:'+=5'});
}





// Expertise page

$('.backtop').mouseover(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#ffffff'});
});

$('.backtop').mouseout(function(){
	TweenMax.to(this,boxsp,{'backgroundColor': '#f1f0ea'});
});

$('.backtop').click(function(){
	TweenMax.to($('html,body'), .8, {'scrollTop':0, ease:Expo.easeInOut});
});

$('.exp-nav-icon').each(function(){
	$(this).mouseover(function(){
		TweenMax.to($(this).children('.show'),boxsp,{alpha:0});
		TweenMax.to($(this).children('.hide'),boxsp,{alpha:1});
	});
	$(this).mouseout(function(){
		TweenMax.to($(this).children('.show'),boxsp,{alpha:1});
		TweenMax.to($(this).children('.hide'),boxsp,{alpha:0});
	});

	$(this).click(function(){
		
		activeSec = $(this).children('img').attr('src').split('icon-')[1];
		activeSection = 'exp-' + activeSec.split('.png')[0];
		console.log(activeSection)
		
		$('section').each(function(){
    		if($(this).attr('id') == activeSection){
    			activeOffset = $(this).offset().top-87;
		    }
		});

		TweenMax.to($('html,body'), .8, {'scrollTop':activeOffset, ease:Expo.easeInOut});

	});
});







// set highlighted nav link

$('#globalNav').children('ul').children('li').each(function(){
	if($(this).text().toLowerCase() == page){
		$(this).addClass('activeLink');
		$(this).text(page);
		
		// tint to off white for Fearless page BG
		if(page == 'fearless'){
			$('body').css('background-color','#f1f0ea');
		}
	}
});





// functions based on page scroll

var startY = 0;
var endY = 500;
var scrollDif;
var shrunk = false;

$(window).scroll(function(){
	//console.log($(this).scrollTop());
	
	// fade hero out on scroll
	if(!isMobile){
		scrollDif = 1-($(this).scrollTop()/topH);
		$('#hero, #hero-tier').css('opacity',scrollDif);
	}
	
	// shrink header
	if($(this).scrollTop()>topH && shrunk == false){
		TweenMax.to($('#globalHeader, #header-bg'), .3, {'height':'73px', ease:Power2.easeOut});
		TweenMax.to($('#logo'), .3, {'marginTop':'10px', ease:Power2.easeOut});
		TweenMax.to($('#social-links'), .3, {'marginTop':'10px', ease:Power2.easeOut});
		TweenMax.to($('#globalNav'), .3, {'marginTop':'10px', ease:Power2.easeOut});
		shrunk = true;
	}
	// expand header
	if($(this).scrollTop()<topH && shrunk == true){
		TweenMax.to($('#globalHeader, #header-bg'), .3, {'height':'100px'});
		TweenMax.to($('#logo'), .3, {'marginTop':'23px'});
		TweenMax.to($('#social-links'), .3, {'marginTop':'17px'});
		TweenMax.to($('#globalNav'), .3, {'marginTop':'15px'});
		shrunk = false;
	}
});

$(document).ready(function(){

	// shrink header
	if($(this).scrollTop()>topH && shrunk == false){
		TweenMax.to($('#globalHeader, #header-bg'), .3, {'height':'60px', ease:Power2.easeOut});
		TweenMax.to($('#logo'), .3, {'marginTop':'2px', ease:Power2.easeOut});
		TweenMax.to($('#social-links'), .3, {'marginTop':'5px', ease:Power2.easeOut});
		TweenMax.to($('#globalNav'), .3, {'marginTop':'8px', ease:Power2.easeOut});
		shrunk = true;
	}
	
	// fade in hero contents
	TweenMax.to('[id^="hero-contents"]', 1, {delay:.5, opacity:1});
})