

$(document).ready(function() {
	$('#addCompanyform').on('submit', function(event) {
		event.preventDefault();
        document.getElementById('msg-box-ajax').style.display = 'block';
		$('#newLinkModal').modal('hide');
		var formData = new FormData();
		formData.append('file', $('#addCompanyImage')[0].files[0]);
		console.log(formData)
		$.ajax({
			data : {
				addCompanyname: $('#addCompanyname').val(),
				addCompanyImage: formData,
				addCompanyType: $('#addCompanyType').val(),
			},
			type : 'POST',
			url : '/addCompany',
			enctype: 'multipart/form-data',
			cache: false,
		})
		.done(function(data) {

			if (data.error) {
                document.getElementById('msg-box-ajax').style.display = 'block';
                document.getElementById('ajax-response').innerHTML = data.error;
			}
			else {
				document.getElementById('msg-box-ajax').style.display = 'block';
				document.getElementById('ajax-response').innerHTML  = data.success;
			}

        });
        event.preventDefault();
    });
    

    $('.explicit-link-delete').on('click', function(event) {
        document.getElementById('msg-box-ajax').style.display = 'block';
		$.ajax({
			data : {
				link_name : $('.explicit-link-delete').attr('id'),
			},
			type : 'POST',
			url : '/app/deletelink/'+ $('.explicit-link-delete').attr('id')
		})
		.done(function(data) {

			if (data.error) {
                document.getElementById('msg-box-ajax').style.display = 'block';
                document.getElementById('ajax-response').innerHTML = data.error;
			}
			else {
				document.getElementById('msg-box-ajax').style.display = 'block';
				document.getElementById('ajax-response').innerHTML  = data.success;
			}

        });
    });
    

    $('.explicit-link-deactive').on('click', function(event) {
        document.getElementById('msg-box-ajax').style.display = 'block';
		$.ajax({
			data : {
				link_name : $('.explicit-link-deactive').attr('id'),
			},
			type : 'POST',
			url : '/app/delink/'+ $('.explicit-link-deactive').attr('id')
		})
		.done(function(data) {

			if (data.error) {
                document.getElementById('msg-box-ajax').style.display = 'block';
                document.getElementById('ajax-response').innerHTML = data.error;
			}
			else {
				document.getElementById('msg-box-ajax').style.display = 'block';
				document.getElementById('ajax-response').innerHTML  = data.success;
			}

        });
        event.preventDefault();
    });
    



    $('.explicit-link-reactive').on('click', function(event) {
		$.ajax({
			data : {
				link_name : $('.explicit-link-reactive').attr('id'),
			},
			type : 'POST',
			url : '/app/reactivatelink/'+ $('.explicit-link-reactive').attr('id')
		})
		.done(function(data) {

			if (data.error) {
                document.getElementById('msg-box-ajax').style.display = 'block';
                document.getElementById('ajax-response').innerHTML = data.error;
			}
			else {
				document.getElementById('msg-box-ajax').style.display = 'block';
				document.getElementById('ajax-response').innerHTML  = data.success;
			}

        });
        event.preventDefault();
	});



});

function hide_msg() {
    document.getElementById('msg-box').style.display = 'none';
    console.log('sdsd');
}

function hide_msg() {
    document.getElementById('msg-box-ajax').style.display = 'none';
    console.log('sdsd');
}

function feature_change(feature_id){
    images = {
        'manageactivity' : "/static/img/manage.png",
        'dataanalytics' :"/static/img/data.png",
        'routing' : "/static/img/routing.png",
        'easysetup' : "/static/img/setup.png",
    }

    document.getElementById('img-features').src = images[feature_id];
    
}

if ($(window).width() > 200) {
	console.log("yaay")
	$(window).scroll(function(){  
	   if ($(this).scrollTop() > 40) {
		  $('#subnav').addClass("fixed-top");
		  // add padding top to show content behind navbar
		  $('#subnav').css('margin-top','0')
		  $('body').css('padding-top', $('.navbar').outerHeight() + 'px');
		}else{
		  $('#subnav').removeClass("fixed-top");
		  $('#subnav').css('margin-top','8px')
		   // remove padding top from body
		  $('body').css('padding-top', '0');
		}   
	});
  }


var uploadField = document.getElementById("company-logo");

uploadField.onchange = function() {
	if(this.files[0].size > 1297152){
		alert("Image is too big! Please upload image of size less than 1mb.");
		this.value = "";
	};
};

