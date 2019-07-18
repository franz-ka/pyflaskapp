$(function(){
    $.fn.datepicker.defaults.format = "dd/mm/yyyy";
    $.fn.datepicker.defaults.language = "es";
})

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
                $.ajax({
                     type: "POST",
                     data: $(form).serialize(),
                     success: function(){
                        form.classList.remove('was-validated');
                        $(form).find('.alert-danger').hide();
                        $(form).find('.alert-success').show();
                        $(form).find('input[type!=hidden]').val('');
                        $(form).find('select').not('.no-form-clear').val(null).trigger('change');
                        $(form).find('.addable.form-group.row').slice(1).remove();
                        if (successcb)
                            successcb()
                        if (formoktout)
                            clearTimeout(formoktout);
                        formoktout = setTimeout( function(){ $(form).find('.alert-success').hide(); } , 5000 );
                     },
                     error: function(r){
                        $(form).find('.alert-success').hide();
                        $(form).find('.alert-danger').show().find('p').html(r.responseText);
                        if (hideErr){
                            if (hideerrtout)
                                clearTimeout(hideerrtout);
                            hideerrtout = setTimeout( function(){ $(form).find('.alert-danger').hide(); } , 5000 );
                        }
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