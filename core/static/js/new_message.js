$(function(){
	var form = $('#messageForm'),
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
    $(".messages_list").mCustomScrollbar();
});