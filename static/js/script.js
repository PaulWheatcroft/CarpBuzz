$(document).ready(function(){
    $(".dropdown-trigger").dropdown();
    $('select').formSelect();
    $('.sidenav').sidenav({
      edge: 'right',
      draggable: true,
      closeOnClick: true
    });
  });