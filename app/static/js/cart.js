
function add(cart, item_cart) {
  cart.push(item_cart);
  commit(cart);
};

function update(cart, item_cart) {
  for (let item of cart) {
    if (item.id == item_cart.id) {
      let pos = cart.indexOf(item);
      cart[pos] = item_cart;
    }
  }
  commit(cart);
};

function remove(cart, item_cart) {
  for (let item of cart) {
    if (item.id == item_cart.id) {
      let pos = cart.indexOf(item);
      cart.splice(pos, 1);
    }
  }
  commit(cart);
}

function commit(cart) {
  localStorage.setItem('cart', JSON.stringify(cart));
}

function itemExist(cart, item_cart) {
  let result = false;
  
  for (let item of cart) {
    
    if (item.id == item_cart.id){
      result = true; 
      break;
    } 
  }
  return result;
}

function update_cart(e) {
  var row = e.currentTarget.closest('tr');
  product_id = row.cells[0].innerHTML;
  name = row.cells[1].innerHTML;
  price = parseFloat(row.cells[5].innerHTML);
  count = parseFloat(row.cells[7].firstChild.value);
  nds = parseInt(row.cells[4].innerHTML);
  btnCart = document.getElementById("btnCart");

  sum = Math.round(count * price * 100) / 100;
  sum_nds = sum - parseFloat((sum * 100 / (100 + nds)).toFixed(2));

  let item_cart = {
    id: product_id,
    name: name,
    qty: count,
    price: price,
    nds: nds,
    sum: sum,
    sum_nds: sum_nds
  };

  cart = localStorage.getItem('cart');

  if (cart == null) cart = [];
  else cart = JSON.parse(cart);

  if (count > 0 && !itemExist(cart, item_cart)) add(cart, item_cart)
  else if (count > 0 && itemExist(cart, item_cart)) update(cart, item_cart);
  else if (count == 0 || isNaN(count) && itemExist(cart, item_cart)) remove(cart, item_cart);

  if (btnCart != null) {
    btnCart.innerHTML = `Корзина ${cart.length}`;
  }

}

function update_pre_order(e) {
  var row = e.currentTarget.closest('tr');
  product_id = row.cells[0].innerHTML;
  name = row.cells[1].innerHTML;
  price = parseFloat(row.cells[3].innerHTML);
  count = parseFloat(row.cells[4].firstChild.value);
  nds = parseInt(row.cells[2].innerHTML);
  btnCart = document.getElementById("btnCart");
  El_total = document.getElementById("total");
  total = parseFloat(El_total.innerHTML);

  sum = Math.round(count * price * 100) / 100;
  sum_nds = sum - parseFloat((sum * 100 / (100 + nds)).toFixed(2));

  let item_cart = {
    id: product_id,
    name: name,
    qty: count,
    price: price,
    nds: nds,
    sum: sum,
    sum_nds: sum_nds
  };

  cart = localStorage.getItem('cart');

  if (cart == null) cart = [];
  else cart = JSON.parse(cart);

  if (count > 0 && !itemExist(cart, item_cart)) add(cart, item_cart)
  else if (count > 0 && itemExist(cart, item_cart)) update(cart, item_cart);
  else if (count == 0 && itemExist(cart, item_cart)) remove(cart, item_cart);

  inequality = parseFloat(row.cells[5].innerHTML) - sum;
  total -= inequality;

  El_total.innerHTML = total == NaN ? "0" : total;
  row.cells[5].innerHTML = sum == NaN ? "0" : sum;
   
}