$(document).ready(function(){
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    $('.datepicker').datepicker();
    $('.sidenav').sidenav({
      edge: 'right',
      draggable: true,
      closeOnClick: true
    });
  });