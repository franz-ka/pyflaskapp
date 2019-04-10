function regFormValid(){
    // html5 constraints - https://www.w3.org/TR/html5/sec-forms.html#constraints
    // bs4 form validation - https://getbootstrap.com/docs/4.0/components/forms/#validation
    var formvalidtout;
    var forms = document.forms;
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
        if (formvalidtout)
            clearTimeout(formvalidtout);
        formvalidtout = setTimeout( function(){ form.classList.remove('was-validated'); } , 3000 );
      }, false);
    });
}

function sel2(clas, placeh, data){
    return $(clas).select2({
        allowClear: true,
        placeholder: placeh,
        width: '100%',
        data: data
    });
}