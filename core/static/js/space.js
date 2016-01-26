$(function(){

	/**
	 * Tworzy message
	 */
	var initMessageForm = (function(){
		var form = $('#messageForm form'),
			btnSubmit = $('.btn', form),
			content = $('textarea[name="content"]', form),
			space = $('input[name="space"]', form),
			file = $('input[name="file"]', form),
			fileSpan = $('.file-input span', form),
			active = false;


		function new_message() {
			var formData = new FormData();
			formData.append('content', content.val());
			formData.append('space', space.val());
			if(file.prop('files')[0]) formData.append('file', file.prop('files')[0]);
			
			$.ajax({
		        url : "/new_message/",
		        type : "POST", 
				cache: false,
       			dataType: 'json',
				processData: false,
				contentType: false,
		        data : formData,

		        success : function(data) {
		            var s = '<div class="messages-item messages-item--new">';
		            s += '<strong class="messages-item_user">'+data.user+'</strong><span class="messages-item_date">'+data.date+'</span>';
		            s += '<button class="messages-item_btn-delete" data-uid="'+data.uid+'"><i class="fa fa-times"></i></button>';
		            s += '<p>'+data.content+'</p>';
					if(file.prop('files')[0]){
						var name = file.prop('files')[0].name,
							extension = name.split(".")[1];
						if(extension=='png' || extension=='jpg' || extension=='bmp'){
							s += '<br><img src="/media/'+file.prop('files')[0].name+'">';
						}else {
							s += '<i class="fa fa-file-o"></i> '+name;
						}
					}
		            s += '</div>';
		            $('.messages_list').removeClass('messages_list--empty');
		            $('.messages_list #mCSB_1_container').prepend(s);
					content.val('');
					file.val('');
					fileSpan.text('');
		            initDeleteMessageForm();
					active = false;
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
		    form.removeClass('is-error');
		    if(content.val()!='' && !active){
		    	active = true;
				new_message();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	/**
	 * Usuwa message
	 */
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

	/**
	 * Edytuje space
	 */
	var initEditForm = (function(){
		var form = $('#editForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			status = $('select[name="status"]', form),
			space = $('input[name="space"]', form);

		function edit_space() {
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
		    	edit_space();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	/**
	 * Tworzy nowy space
	 */
	var initNewSpaceForm = (function(){
		var form = $('#newSpaceForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			space = $('input[name="space"]', form),
			users = $('input[name="new_space_users_id"]', form);

		function new_space() {
			var checkedUsers = [];
			users.each(function(){
				if($(this).prop('checked')) checkedUsers.push($(this).val());
			});
			
		    $.ajax({
		        url : "/new_space/",
		        type : "POST", 
		        data : { 'space':  space.val(), 'name': name.val(), 'description': description.val(), 'new_space_users_id': checkedUsers },

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
		    	new_space();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	/**
	 * Tworzy nowy kanał
	 */
	var initNewChannelForm = (function(){
		var form = $('#newChannelForm form'),
			btnSubmit = $('.btn', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			space = $('input[name="space"]', form);

		function new_channel() {
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
		    	new_channel();
		    }else{
		    	form.addClass('is-error');
		    }
		});
	});
	
	/**
	 * Koloruje userów
	 */
	var initUsers = (function(){
    	function getRandomInt(min, max) {
    	    return Math.floor(Math.random() * (max - min + 1)) + min;
    	}
    	function losuj(){
	    	var r, g, b,
	    		pos = Math.round(getRandomInt(0,2));

	    	if(pos == 0){
	    		r = 247;
	    		g = Math.round(getRandomInt(124,246));
	    		b = 123;
	    	}else if(pos == 1){
	    		r = 247;
	    		g = 123;
	    		b = Math.round(getRandomInt(124,246));
	    	}else{
	    		r = 123;
	    		g = Math.round(getRandomInt(124,246));
	    		b = 247;
	    	}
	    	return 'rgb('+r+','+g+','+b+')';
	    }

    	$('.current-space_avatar').each(function(id){
    		var t = $(this);
    		t.css('background', losuj());
    		t.on('mouseover',function(){
    			t.width(t.prop('scrollWidth'));
    		});
    		t.on('mouseout',function(){
    			t.width(35);
    		});
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
	initUsers();

	$('.popup_btn-close').on('click',function(){
		closePopup('#'+$(this).parent().prop('id'));
	});
	$('.file-input').on('click',function(){
		var btn = $(this).find('.file-input_btn'),
			span = $(this).find('span');
			
		btn.on('change',function(event){
			span.text($('.file-input input').val());
		});
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