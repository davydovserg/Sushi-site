// Новинки, которых нет в магазине InSales. Фото положить в cut/ и указать в img.
(function(){
  const add = (cat, items) => { const c = window.MENU.find(x => x.id === cat); if (c) c.items.unshift(...items); };
  add('teplye-rolly', [
    {id:'new-tempura-ugor', t:'Ролл Темпура с угрём', d:'Рис, нори, огурец, угорь, сыр, майонез, кляр, сухари, унаги соус.', p:499, w:'', img:'cut/soon.svg', n:1},
    {id:'new-tempura-losos', t:'Ролл Темпура с лососем', d:'Рис, нори, огурец, лосось, краб, сыр, майонез, кляр, сухари.', p:499, w:'', img:'cut/soon.svg', n:1}
  ]);
  add('katalog-1-bbda54', [
    {id:'new-zap-midii', t:'Запечённые мидии', d:'Рис, сыр Филадельфия, огурец, мясо мидии, яки соус, белый кунжут.', p:479, w:'', img:'cut/soon.svg', n:1},
    {id:'new-zap-kalmar', t:'Запечённый кальмар', d:'Рис, сыр Филадельфия, огурец, кальмар, унаги соус, белый кунжут.', p:479, w:'', img:'cut/soon.svg', n:1}
  ]);
})();
