

$(document).ready(function() {
	$('#createURLform').on('submit', function(event) {
        document.getElementById('msg-box-ajax').style.display = 'block';
        $('#newLinkModal').modal('hide');
		$.ajax({
			data : {
				link_name : $('#link_name').val(),
				long_link : $('#long_link').val()
			},
			type : 'POST',
			url : '/app/createnewurl'
		})
		.done(function(data) {

			if (data.error) {
                document.getElementById('msg-box-ajax').style.display = 'block';
                document.getElementById('ajax-response').innerHTML = data.error;
			}
			else {
				document.getElementById('msg-box-ajax').style.display = 'block';
				document.getElementById('ajax-response').innerHTML  = 'Url shortended and is available at: ' + `<a href = '${data.url}'>${data.url}</a>`;
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
        event.preventDefault();
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