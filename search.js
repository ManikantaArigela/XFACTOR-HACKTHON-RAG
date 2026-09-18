(() => {
  const form = document.querySelector("[data-product-search]");
  if (!form) return;

  const input = form.querySelector("input[name='q']");
  const shopUrl = "shop-tailwind.html";
  const query = new URLSearchParams(window.location.search).get("q")?.trim() || "";
  if (input && query) input.value = query;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = input.value.trim();
    if (window.location.pathname.endsWith("shop-tailwind.html")) {
      window.history.replaceState({}, "", value ? `${shopUrl}?q=${encodeURIComponent(value)}` : shopUrl);
      filterProducts(value);
      return;
    }
    window.location.href = value ? `${shopUrl}?q=${encodeURIComponent(value)}` : shopUrl;
  });

  if (window.location.pathname.endsWith("shop-tailwind.html")) filterProducts(query);

  function filterProducts(value) {
    const normalized = value.toLowerCase();
    const products = [...document.querySelectorAll("[data-product-card]")];
    let visibleCount = 0;
    products.forEach((product) => {
      const matches = !normalized || product.textContent.toLowerCase().includes(normalized);
      product.hidden = !matches;
      if (matches) visibleCount += 1;
    });

    let emptyState = document.querySelector("[data-search-empty]");
    if (!emptyState) {
      emptyState = document.createElement("p");
      emptyState.dataset.searchEmpty = "true";
      emptyState.className = "col-span-full py-12 text-center text-slate-500";
      document.querySelector("[data-product-grid]").appendChild(emptyState);
    }
    emptyState.textContent = normalized
      ? `No products found for “${value}”.`
      : "No products available.";
    emptyState.hidden = visibleCount !== 0;
  }
})();
