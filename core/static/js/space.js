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

	function sendForm(form, url, callback){
		var f = new FormData(form[0]);
	    $.ajax({
	        url : url,
	        type : "POST",
   			dataType: 'json',
			cache: false,
			processData: false,
			contentType: false,
	        data : f,

	        success : function(data) {
	        	callback(data);
	        },

	        error : function(xhr,errmsg,err) {
	            console.log(xhr.status + ": " + xhr.responseText);
	        }
	    });
	}

	/**
	 * Edycja space
	 */
	var initEditForm = (function(){
		var form = $('#editForm form'),
			btn =  $('input[type="submit"]', form),
			name = $('input[name="name"]', form),
			description = $('textarea[name="description"]', form),
			sent = false;

		form.on('submit', function(event){
		    event.preventDefault();

		    form.removeClass('is-error');

		    if(name.val()!=''){
		    	sent = true;
		    	btn.prop('disabled', true);

		    	sendForm(form, '/edit_space/', function(data){
					closePopup('#popupEditSpace');

	        		$('.current-space_head h1').text(name.val());
	        		$('.current-space_desc p').text(description.val());

		    		sent = false;
		    		btn.prop('disabled', false);
				})

		    }else{
		    	form.addClass('is-error');
		    }
		});
	});

	/**
	 * Tworzenie nowego space
	 */
	var initNewSpaceForm = (function(){
		var form = $('#newSpaceForm form'),
			name = $('input[name="name"]', form),
			btn =  $('input[type="submit"]', form),
			mySubspaces = $('#mySubspaces'),
			sent = false;

		form.on('submit', function(event){
		    event.preventDefault();

		    form.removeClass('is-error');

		    if(name.val()!=''){
		    	sent = true;
		    	btn.prop('disabled', true);

		    	sendForm(form, '/new_space/', function(data){
					closePopup('#popupNewSpace');

		    		if(mySubspaces.hasClass('list-space--empty')){
		    			mySubspaces.removeClass('list-space--empty').html('<div class="list-space_item"></div><div class="list-space_item"></div><div class="list-space_item"></div><div class="list-space_item"></div>');
		    		}
		    		mySubspaces.find('.list-space_item:empty').eq(0).before('<div class="list-space_item list-space_item--new"><a href="/'+data.space+'">'+name.val()+'</a></div>');

		    		sent = false;
		    		btn.prop('disabled', false);
		    		form[0].reset();
				})
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
    	$('.current-space_avatar').each(function(id){
    		var t = $(this);
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
	initEditForm();
	initAddCollaborators();
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
