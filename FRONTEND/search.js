(() => {
  const form = document.querySelector("[data-product-search]");
  if (!form) return;

  const input = form.querySelector("input[name='q']");
  const grid = document.querySelector("[data-product-grid]");
  const shopUrl = "shop-tailwind.html";
  const apiBase = window.ARUDHRA_API_BASE_URL || "http://127.0.0.1:5000/api";
  const apiOrigin = new URL(apiBase).origin;
  const query = new URLSearchParams(window.location.search).get("q")?.trim() || "";
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

  if (window.location.pathname.endsWith("shop-tailwind.html")) loadProducts(query);

  async function loadProducts(value) {
    if (!grid) return;
    try {
      const endpoint = value
        ? `${apiBase}/search?q=${encodeURIComponent(value)}&limit=50`
        : `${apiBase}/content/?limit=50`;
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
      showMessage(value ? `No uploaded products found for “${value}”.` : "No uploaded products available.");
      return;
    }
    products.forEach((product) => {
      const card = document.createElement("article");
      card.className = "bg-white rounded-lg shadow-sm overflow-hidden";
      const image = product.image_path ? new URL(product.image_path, apiOrigin).href : "https://via.placeholder.com/600x400?text=Product";
      card.innerHTML = `
        <img src="${escapeHtml(image)}" alt="${escapeHtml(product.title)}" class="w-full h-44 object-cover">
        <div class="p-4">
          <h3 class="font-semibold">${escapeHtml(product.title)}</h3>
          <p class="text-sm text-slate-500">${escapeHtml(product.description)}</p>
          <p class="mt-2 text-xs text-slate-400">${escapeHtml(product.category)}</p>
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
})();
