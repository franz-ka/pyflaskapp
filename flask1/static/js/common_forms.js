$(function(){
    $.fn.datepicker.defaults.format = "dd/mm/yyyy";
    $.fn.datepicker.defaults.language = "es";
})

function lockForm(form){
    $(form).find('input,select,button').each(function(){
        var prePostDis = $(this).prop('disabled') || false
        $(this).data('pre-post-disabled', prePostDis);
        $(this).prop('disabled', true)
    })
    $(form).parents('.card').attr('style', 'background-color: #d7dde3 !important')
    $(document.body).css('cursor', 'progress')
}
function unlockForm(form){
    $(form).find('input,select,button').each(function(){
        var prePostDis = $(this).data('pre-post-disabled') || false
        $(this).prop('disabled', prePostDis)
        $(this).data('pre-post-disabled', null);
    })
    $(form).parents('.card').attr('style', null)
    $(document.body).css('cursor', 'inherit')
}

function regFormValid(hideErr, successcb){
    // html5 constraints - https://www.w3.org/TR/html5/sec-forms.html#constraints
    // bs4 form validation - https://getbootstrap.com/docs/4.0/components/forms/#validation
    var forms = document.forms;
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
        var formvalidtout, formoktout, hideerrtout;
        console.log('regFormValid', form)
        form.addEventListener('submit', function(event) {
            if (form.checkValidity() === false) {
              event.preventDefault();
              event.stopPropagation();
            }else{
                event.preventDefault();
                formData = $(form).serialize()
                lockForm(form)
                $.ajax({
                     type: "POST",
                     data: formData,
                     success: function(r){
                        form.classList.remove('was-validated');
                        $(form).find('.alert-warning').hide();
                        $(form).find('.alert-danger').hide();
                        $(form).find('input[type!=hidden]').val('');
						$(form).find('input[type=checkbox]').prop('checked', false)
                        $(form).find('select').not('.no-form-clear').val(null).trigger('change');
                        $(form).find('.addable.form-group.row').slice(1).remove();
                        if (successcb)
                            successcb()
                        if (formoktout)
                            clearTimeout(formoktout);
						if (!r){
	                        $(form).find('.alert-success').show();
							formoktout = setTimeout( function(){ $(form).find('.alert-success').hide(); } , 5000 );
						}else{
                        	$(form).find('.alert-warning').show().find('p').html(r);
							formoktout = setTimeout( function(){ $(form).find('.alert-warning').hide(); } , 10000 );
						}
                     },
                     error: function(r){
                        $(form).find('.alert-success').hide();
                        $(form).find('.alert-warning').hide();
                        $(form).find('.alert-danger').show().find('p').html(r.responseText);
                        if (hideErr){
                            if (hideerrtout)
                                clearTimeout(hideerrtout);
                            hideerrtout = setTimeout( function(){ $(form).find('.alert-danger').hide(); } , 5000 );
                        }
                     },
                     complete: function(){
                        unlockForm(form);
                     }
                });
            }
            form.classList.add('was-validated');
            if (formvalidtout)
                clearTimeout(formvalidtout);
            formvalidtout = setTimeout( function(){ form.classList.remove('was-validated'); } , 5000 );
        }, false);//addEventListener
    });//filter.call
}

function sel2(clas, placeh, data){
    return $(clas).select2({
        allowClear: true,
        placeholder: placeh,
        width: '100%',
        data: data
    });
}

// How can I add or update a query string parameter?
// https://stackoverflow.com/questions/5999118/how-can-i-add-or-update-a-query-string-parameter
function UpdateQueryString(key, value, url) {
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
        hash;

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null) {
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        }
        else {
            hash = url.split('#');
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
                url += '#' + hash[1];
            }
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?';
            hash = url.split('#');
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
                url += '#' + hash[1];
            }
            return url;
        }
        else {
            return url;
        }
    }
}
