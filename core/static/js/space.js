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
							s += '<br><i class="fa fa-file-o"></i> '+name;
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
			space = $('input[name="space"]', form);

		function edit_space() {
		    $.ajax({
		        url : "/edit_space/",
		        type : "POST",
		        data : { 'space':  space.val(), 'name': name.val(), 'description': description.val() },

		        success : function(data) {
		        	if(data){
		        		closePopup('#popupEditSpace');
		        		$('.current-space h1').text(name.val());
		        		$('.current-space p').text(description.val());
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
	var initAddCollaborators = (function(){
		var form = $('#addCollaboratorsForm form'),
			btnSubmit = $('.btn', form),
			space = $('input[name="space"]', form),
			users = $('input[name="new_collaborators_id"]', form),
			usersNames = $('.checkbox-wrapper label', form);

		function add_collaborators() {
			var checkedUsers = [],
				checkedUsersId = [];

			users.each(function(index){
				if($(this).prop('checked')){
					checkedUsers.push($(this).val());
					checkedUsersId.push(index);
				}
			});

		    $.ajax({
		        url : "/add_collaborators/",
		        type : "POST",
		        data : { 'space':  space.val(), 'new_collaborators_id': checkedUsers },

		        success : function(data) {
		        	if(data){
		        		closePopup('#popupAddCollaborators');
						$.each(checkedUsersId, function(index){
							var name = usersNames.eq(checkedUsersId[index]).text();
							$('.checkbox-wrapper', form).eq(checkedUsersId[index]).css('display','none');
							$('.current-space_users').append('<div class="current-space_avatar"><strong>'+name.substr(1,1)+'</strong><span>'+name+'</span></div>');
						});
						users.each(function(index){
							$(this).prop('checked', false);
						});
						initUsers();
		        	}
		        },

		        error : function(xhr,errmsg,err) {
		            console.log(xhr.status + ": " + xhr.responseText);
		        }
		    });
		};
		form.on('submit', function(event){
		    event.preventDefault();
			add_collaborators();
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

    	$('.current-space .user-avatar').each(function(id){
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

	var initCommunicator = (function(){
		var users = $('.communicator_users .user-avatar'),
			t;
		users.each(function(index){
			t = index*0.1 + 's';
			$(this).css('transition-delay', t);
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

	initBreadcrumbs();
	initMessageForm();
	initDeleteMessageForm();
	initNewSpaceForm();
	initEditForm();
	initAddCollaborators();
	initUsers();
	initCommunicator();

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

	$('.checkbox-wrapper').on('click', function(){
		var t = $(this).find('input');
		if(t.prop('checked')){
			t.prop('checked', false);
			$(this).removeClass('is-active');
		}else {
			t.prop('checked', true);
			$(this).addClass('is-active');
		}
	});

	$('.checkbox-wrapper').each(function(){
		if($(this).find('input').prop('checked')){
			$(this).addClass('is-active');
		}
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
	$('#btnAddCollaborators').on('click', function(event){
		event.preventDefault();
		openPopup('#popupAddCollaborators');
	})

    $(".messages_list").mCustomScrollbar();
});
