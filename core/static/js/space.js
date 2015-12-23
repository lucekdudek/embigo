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
		            s += '<button class="messages-item_btn-delete" data-uid="'+data.uid+'"><i class="fa fa-times"></i></button>';
		            s += '<p>'+data.content+'</p>';
		            s += '</div>';
		            $('.messages_list').removeClass('messages_list--empty');
		            $('.messages_list #mCSB_1_container').prepend(s);
		            initDeleteMessageForm();
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

	var initDeleteMessageForm = (function(){
		var btns = $('.messages-item_btn-delete');

		function delete_message(uid, item) {
		    $.ajax({
		        url : "/delete_message/",
		        type : "POST", 
		        data : { 'message': uid },

		        success : function(data) {
					if(data){
						item.on('webkitAnimationEnd oanimationend msAnimationEnd animationend', function(){
							$(this).remove();
						});
						item.addClass('messages-item--delete');
					}
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		btns.on('click', function(event){
		    delete_message($(this).attr('data-uid'), $(this).parent());
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
		    if(name.val()!=''){
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
		        		if($('#mySubspaces').hasClass('list-space--empty')) $('#mySubspaces').removeClass('list-space--empty').text('');
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
		    if(name.val()!=''){
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
		        		if($('#myChannels').hasClass('list-space--empty')) $('#myChannels').removeClass('list-space--empty').text('');
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
		    if(name.val()!=''){
		    	new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	var initBreadcrumbs = (function(){
		if($('.breadcrumbs ul').prop('scrollWidth')>$('.breadcrumbs').width()){
			$('.breadcrumbs').addClass('breadcrumbs--hide');
		}
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

	initBreadcrumbs();
	initMessageForm();
	initDeleteMessageForm();
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