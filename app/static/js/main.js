function onLoadDocument(e) {
  if (document.location.pathname == '/catalog') {
    cartStr = localStorage.getItem('cart');
    if (cartStr != null) {
      cart = JSON.parse(cartStr);
      btnCart = document.getElementById('btnCart');
      btnCart.innerHTML = `Корзина ${cart.length}`;
    }
  }
}

function clickOrders(e) {
  var row = e.currentTarget.closest('tr');
  rejected = (e.target.id == 'btnOrderRejected');
  for (var i = 0; i < row.childNodes.length; i++) {
    if (row.childNodes[i].id == "order_id" && !rejected) {
      document.location.href = `/orders/order/${row.childNodes[i].innerHTML}`;
    }
  }

  if (rejected) document.location.href = e.target.attributes.href.value;

}

function preOrder(e) {
  btnCart = document.getElementById('btnCart')
  btnCreateOrder = document.getElementById('btnCreateOrder')
  cartStr = localStorage.getItem('cart');
  if (cartStr != null && btnCart != null) {
    btnCart.value = cartStr;
  } else if (cartStr != null && btnCreateOrder != null) {
    btnCreateOrder.value = cartStr;
  }
  localStorage.clear();
}

function for_table(e) {
  pre_order = document.getElementById("OrderItems");
  for (var i = 0; i < pre_order.childNodes.length; i++) {
    consolo.log(pre_order.childNodes[i]);
  }
}

function product_info(e) {
  var row = e.currentTarget.closest('tr');
  product_id = row.cells[0].innerHTML;
  description = document.getElementById("productDescription")
  product_name = document.getElementById("productName")

  fetch('/catalog/curr_product/info?product_id=' + product_id).then(function (response) {
    response.json().then(function (data) {
      if (description != null && product_name != null) {
        description.innerHTML = data.description;
        product_name.innerHTML = data.name;
      }
    });
  });
}

$('#myModal').on('hidden.bs.modal', function (event) {
  form.submit()
});