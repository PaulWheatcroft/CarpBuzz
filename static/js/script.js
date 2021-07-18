/* scripts initialise once the document has loaded */
$(document).ready(function(){
    /* Materialize form elements  */
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    $('.datepicker').datepicker({
      format: "dd-mmm-yyyy"
    });
    $('.timepicker').timepicker({
      twelveHour: false
    });
    /* Materialize side navigation on  mobile devices  */
    $('.sidenav').sidenav({
      edge: 'right',
      draggable: true,
      closeOnClick: true
    });
    /* Materialize modal  */
    $('.modal').modal();
  });
