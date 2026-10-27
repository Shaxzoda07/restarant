(function () {
  var data = JSON.parse(document.getElementById('dish-data').textContent);
  var cart = {};
  try { cart = JSON.parse(localStorage.getItem('novza_cart') || '{}'); } catch (e) { cart = {}; }
  Object.keys(cart).forEach(function (id) { if (!data[id]) delete cart[id]; });

  var $ = function (s) { return document.querySelector(s); };
  var itemsEl = $('#cart-items'), emptyEl = $('#cart-empty'), form = $('#order-form');
  var countEl = $('#cart-count'), totalEl = $('#cart-total'), btn = $('#cart-btn');
  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };

  function save() { try { localStorage.setItem('novza_cart', JSON.stringify(cart)); } catch (e) {} }
  function open() { document.body.classList.add('cart-open'); }
  function close() { document.body.classList.remove('cart-open'); }

  function render() {
    var ids = Object.keys(cart), count = 0, total = 0, html = '';
    ids.forEach(function (id) {
      var d = data[id], q = cart[id]; count += q; total += d.price * q;
      html += '<div class="ci"><div class="ci-info"><b>' + d.name + '</b><small>' + fmt(d.price * q) + ' so‘m</small></div>' +
        '<div class="qty"><button type="button" data-d="-1" data-id="' + id + '">−</button><span>' + q +
        '</span><button type="button" data-d="1" data-id="' + id + '">+</button></div></div>';
    });
    itemsEl.innerHTML = html;
    countEl.textContent = count;
    totalEl.textContent = fmt(total) + ' so‘m';
    emptyEl.hidden = ids.length > 0;
    form.hidden = ids.length === 0;
    save();
  }

  function add(id) {
    cart[id] = (cart[id] || 0) + 1;
    render();
    btn.classList.remove('bump'); void btn.offsetWidth; btn.classList.add('bump');
    window.toast('✓ ' + data[id].name + ' savatga qo‘shildi');
  }

  function syncType() {
    var v = document.querySelector('input[name=otype]:checked').value;
    $('#f-table').hidden = v !== 'dine';
    $('#f-address').hidden = v !== 'delivery';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('.add');
    if (a) {
      add(a.dataset.id);
      a.classList.add('ok'); a.textContent = '✓';
      setTimeout(function () { a.classList.remove('ok'); a.textContent = '+'; }, 900);
      return;
    }
    var q = e.target.closest('.qty button');
    if (q) {
      var id = q.dataset.id; cart[id] += parseInt(q.dataset.d, 10);
      if (cart[id] <= 0) delete cart[id];
      render(); return;
    }
    var t = e.target.closest('.table');
    if (t && !t.disabled) {
      document.querySelectorAll('.table.selected').forEach(function (x) { x.classList.remove('selected'); });
      t.classList.add('selected');
      $('#f-table').value = t.dataset.id;
      document.querySelector('input[name=otype][value=dine]').checked = true;
      syncType();
      window.toast('Stol tanlandi. Endi menyudan taom tanlang');
      document.getElementById('menu').scrollIntoView();
    }
  });
  btn.addEventListener('click', open);
  $('#close-cart').addEventListener('click', close);
  $('#overlay').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  var tabs = document.querySelectorAll('.tab'), cats = document.querySelectorAll('.menu-cat');
  var activeCat = 'all';
  function filter() {
    var q = $('#search').value.trim().toLowerCase(), shown = 0;
    cats.forEach(function (c) {
      var catOk = activeCat === 'all' || c.dataset.cat === activeCat, any = false;
      c.querySelectorAll('.dish').forEach(function (d) {
        var ok = catOk && (!q || d.dataset.name.indexOf(q) > -1);
        d.style.display = ok ? '' : 'none';
        if (ok) { any = true; d.classList.add('in'); }
      });
      c.style.display = any ? '' : 'none';
      if (any) shown++;
    });
    $('#no-result').hidden = shown > 0;
  }
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.classList.remove('active'); });
      t.classList.add('active'); activeCat = t.dataset.cat; filter();
    });
  });
  $('#search').addEventListener('input', filter);

  document.querySelectorAll('input[name=otype]').forEach(function (r) { r.addEventListener('change', syncType); });
  syncType();

  try {
    $('#f-name').value = localStorage.getItem('novza_name') || '';
    $('#f-phone').value = localStorage.getItem('novza_phone') || '';
  } catch (e) {}

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var err = $('#form-error'); err.hidden = true;
    var sb = $('#submit-order'); sb.disabled = true; sb.textContent = 'Yuborilmoqda…';
    var payload = {
      items: Object.keys(cart).map(function (id) { return { id: id, qty: cart[id] }; }),
      order_type: document.querySelector('input[name=otype]:checked').value,
      table: $('#f-table').value, name: $('#f-name').value, phone: $('#f-phone').value,
      address: $('#f-address').value, comment: $('#f-comment').value
    };
    var token = document.querySelector('meta[name=csrf-token]').content;
    fetch('/order/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (res.ok) {
        try { localStorage.setItem('novza_name', payload.name); localStorage.setItem('novza_phone', payload.phone); } catch (e) {}
        cart = {}; save(); window.location = res.url;
      } else {
        err.textContent = res.error || 'Xatolik yuz berdi'; err.hidden = false;
        sb.disabled = false; sb.textContent = 'Buyurtma berish';
      }
    }).catch(function () {
      err.textContent = 'Tarmoq xatosi. Qaytadan urinib ko‘ring.'; err.hidden = false;
      sb.disabled = false; sb.textContent = 'Buyurtma berish';
    });
  });

  render();
})();
