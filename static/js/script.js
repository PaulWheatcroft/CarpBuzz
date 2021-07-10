$(document).ready(function(){
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    $('.datepicker').datepicker({
      format: "dd-mmm-yyyy"  
    });
    $('.sidenav').sidenav({
      edge: 'right',
      draggable: true,
      closeOnClick: true
    });
  });
