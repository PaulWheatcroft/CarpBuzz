$(document).ready(function(){
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    $('.datepicker').datepicker({
      format: "dd-mmm-yyyy"  
    });
    $('.timepicker').timepicker({
      twelveHour: false
    });
    $('.sidenav').sidenav({
      edge: 'right',
      draggable: true,
      closeOnClick: true
    });
    $('.modal').modal();
  });
