$(function(){

	var initMessageForm = (function(){
		var form = $('#messageForm form'),
			btnSubmit = $('.btn', form),
			content = $('textarea[name="content"]', form),
			space = $('input[name="space"]', form);

		function new_message() {
		    $.ajax({
		        url : "/new_message/",
		        type : "POST", 
		        data : { 'space':  space.val(), 'content': content.val() },

		        success : function(data) {
					content.val('');
		            var s = '<div class="messages-item messages-item--new">';
		            s += '<strong class="messages-item_user">'+data.user+'</strong><span class="messages-item_date">'+data.date+'</span>';
		            s += '<p>'+data.content+'</p>';
		            s += '</div>';
		            $('.messages_list').removeClass('messages_list--empty');
		            $('.messages_list #mCSB_1_container').prepend(s);
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
		    form.removeClass('is-error');
		    if(content.val()!=''){
		    	new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	var initEditForm = (function(){
		var form = $('#editForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			status = $('select[name="status"]', form),
			space = $('input[name="space"]', form);

		function new_message() {
		    $.ajax({
		        url : "/edit_space/",
		        type : "POST", 
		        data : { 'space':  space.val(), 'name': name.val(), 'description': description.val(), 'status': status.val() },

		        success : function(data) {
		        	if(data){
		        		closePopup('#popupEditSpace');
		        		$('.current-space h1').text(name.val());
		        		$('.current-space p').text(description.val());
		        		if(status.val()==2){
		        			$(".current-space").addClass("current-space--archive");
		        		}else{
		        			$(".current-space").removeClass("current-space--archive");
		        		}
		        	}
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
		    form.removeClass('is-error');
		    if(name.val()!='' && description.val()!=''){
		    	new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	var initNewSpaceForm = (function(){
		var form = $('#newSpaceForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			space = $('input[name="space"]', form);

		function new_message() {
		    $.ajax({
		        url : "/new_space/",
		        type : "POST", 
		        data : { 'space':  space.val(), 'name': name.val(), 'description': description.val() },

		        success : function(data) {
		        	if(data){
		        		closePopup('#popupNewSpace');
		        		$('#mySubspaces').append('<a href="/'+data.space+'" class="list-space_item list-space_item--new">'+name.val()+'</a>');
		        		name.val('');
		        		description.val('');
		        	}
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
		    form.removeClass('is-error');
		    if(name.val()!='' && description.val()!=''){
		    	new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	var initNewChannelForm = (function(){
		var form = $('#newChannelForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			space = $('input[name="space"]', form);

		function new_message() {
		    $.ajax({
		        url : "/new_channel/",
		        type : "POST", 
		        data : { 'space':  space.val(), 'name': name.val(), 'description': description.val() },

		        success : function(data) {
		        	if(data){
		        		closePopup('#popupNewChannel');
		        		$('#myChannels').append('<a href="/'+data.space+'" class="list-space_item list-space_item--new">'+name.val()+'</a>');
		        		name.val('');
		        		description.val('');
		        	}
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
		    form.removeClass('is-error');
		    if(name.val()!='' && description.val()!=''){
		    	new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	var openPopup = function(popup){
		$('.popup-bg').fadeIn(function(){
			$(popup).fadeIn();
		});
	};

	var closePopup = function(popup){
		$(popup).fadeOut(function(){
			$('.popup-bg').fadeOut();
		});
	};


	initMessageForm();
	initNewSpaceForm();
	initNewChannelForm();
	initEditForm();

	$('.popup_btn-close').on('click',function(){
		closePopup('#'+$(this).parent().prop('id'));
	});

	$('#btnEditSpace').on('click', function(event){
		event.preventDefault();
		openPopup('#popupEditSpace');
	})
	$('#btnNewSpace').on('click', function(event){
		event.preventDefault();
		openPopup('#popupNewSpace');
	})
	$('#btnNewChannel').on('click', function(event){
		event.preventDefault();
		openPopup('#popupNewChannel');
	})

    $(".messages_list").mCustomScrollbar();
});