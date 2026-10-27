(function () {
  if (!/\/restaurant\/order\/$/.test(location.pathname)) return;
  var dirty = false;
  document.addEventListener('change', function () { dirty = true; });
  setInterval(function () {
    var a = document.activeElement;
    if (dirty || (a && /^(INPUT|SELECT|TEXTAREA)$/.test(a.tagName))) return;
    location.reload();
  }, 30000);
})();
