(() => {
  const form = document.querySelector("[data-product-search]");
  const grid = document.querySelector("[data-product-grid]");
  const shopUrl = "shop-tailwind.html";
  const apiBase = window.ARUDHRA_API_BASE_URL || "http://127.0.0.1:5000/api";
  const query = new URLSearchParams(window.location.search).get("q")?.trim() || "";

  if (form) {
    const input = form.querySelector("input[name='q']");
    if (input && query) input.value = query;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const value = input.value.trim();
      if (window.location.pathname.endsWith("shop-tailwind.html")) {
        window.history.replaceState({}, "", value ? `${shopUrl}?q=${encodeURIComponent(value)}` : shopUrl);
        await loadProducts(value);
        return;
      }
      window.location.href = value ? `${shopUrl}?q=${encodeURIComponent(value)}` : shopUrl;
    });
  }

  if (window.location.pathname.endsWith("shop-tailwind.html") || grid) {
    loadProducts(query);
  }

  async function loadProducts(value) {
    if (!grid) return;
    try {
      const endpoint = value
        ? `${apiBase}/search?q=${encodeURIComponent(value)}&limit=50`
        : `${apiBase}/products?limit=50`;
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      const payload = await response.json();
      const products = value ? payload.data?.results || [] : payload.data?.items || [];
      renderProducts(products, value);
    } catch (_error) {
      filterDemoProducts(value);
    }
  }

  function renderProducts(products, value) {
    grid.innerHTML = "";
    if (!products.length) {
      showMessage(value ? `No products found matching “${value}”.` : "No products available in catalog.");
      return;
    }
    products.forEach((product) => {
      const card = document.createElement("article");
      card.className = "bg-white rounded-xl shadow-sm hover:shadow-md transition border border-slate-100 overflow-hidden flex flex-col justify-between";
      
      // Clean mobile hardware photo for showcase
      const image = product.image_path || "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800";
      const formattedPrice = product.price ? `₹${Number(product.price).toLocaleString('en-IN')}` : "Contact Store";
      const specsSummary = [product.brand, product.ram, product.storage].filter(Boolean).join(" · ");

      card.innerHTML = `
        <div class="relative bg-slate-100/60 aspect-[4/3] overflow-hidden flex items-center justify-center p-3">
          <img src="${escapeHtml(image)}" alt="${escapeHtml(product.title || product.name)}" class="w-full h-full object-contain hover:scale-105 transition duration-300">
          <span class="absolute top-2 left-2 bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Product Showcase</span>
        </div>
        <div class="p-4 flex-1 flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-slate-800 text-base leading-snug">${escapeHtml(product.title || product.name)}</h3>
            <p class="text-xs text-slate-500 mt-1 line-clamp-2">${escapeHtml(product.description || specsSummary)}</p>
            ${specsSummary ? `<div class="mt-2 text-xs font-semibold text-slate-400 bg-slate-50 inline-block px-2 py-1 rounded-md border border-slate-100">${escapeHtml(specsSummary)}</div>` : ''}
          </div>
          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
            <div>
              <span class="text-xs text-slate-400 block">Arudhra Price</span>
              <span class="font-bold text-lg text-slate-900">${formattedPrice}</span>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="addToCart('${escapeHtml(product.id)}', '${escapeHtml(product.title || product.name)}', ${product.price || 0})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-3 py-2 rounded-lg transition shadow-sm">
                Add to Cart
              </button>
            </div>
          </div>
        </div>`;
      grid.appendChild(card);
    });
  }

  function filterDemoProducts(value) {
    const normalized = value.toLowerCase();
    const products = [...grid.querySelectorAll("[data-product-card]")];
    let visibleCount = 0;
    products.forEach((product) => {
      const matches = !normalized || product.textContent.toLowerCase().includes(normalized);
      product.hidden = !matches;
      if (matches) visibleCount += 1;
    });

    let emptyState = grid.querySelector("[data-search-empty]");
    if (!emptyState) {
      emptyState = document.createElement("p");
      emptyState.dataset.searchEmpty = "true";
      emptyState.className = "col-span-full py-12 text-center text-slate-500";
      grid.appendChild(emptyState);
    }
    emptyState.textContent = normalized ? `No products found for “${value}”.` : "No products available.";
    emptyState.hidden = visibleCount !== 0;
  }

  function showMessage(message) {
    const emptyState = document.createElement("p");
    emptyState.className = "col-span-full py-12 text-center text-slate-500";
    emptyState.textContent = message;
    grid.appendChild(emptyState);
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (character) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;",
    }[character]));
  }

  // Global Cart helper
  window.addToCart = (id, name, price) => {
    alert(`Added "${name}" (₹${price.toLocaleString('en-IN')}) to your cart!`);
  };
})();
