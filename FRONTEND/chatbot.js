(() => {
  const apiBase = window.ARUDHRA_API_BASE_URL || "http://127.0.0.1:5000/api";

  // Create Chatbot UI HTML Container
  const chatContainer = document.createElement("div");
  chatContainer.id = "arudhra-rag-chatbot-root";
  chatContainer.className = "fixed bottom-5 right-5 z-50 font-sans";

  chatContainer.innerHTML = `
    <!-- Floating Chat Trigger Button -->
    <button id="rag-chat-toggle" class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold px-4 py-3 rounded-full shadow-2xl flex items-center gap-2.5 transition-all transform hover:scale-105">
      <div class="relative flex items-center justify-center">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
        <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full animate-ping"></span>
        <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
      </div>
      <span>Ask Store AI</span>
    </button>

    <!-- Chat Modal Window -->
    <div id="rag-chat-window" class="hidden fixed bottom-20 right-5 w-96 max-w-[calc(100vw-2.5rem)] h-[540px] bg-white rounded-2xl shadow-2xl border border-slate-100 flex flex-col overflow-hidden transition-all duration-300">
      
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-600 text-white p-4 flex items-center justify-between shadow-md">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-lg font-bold">🤖</div>
          <div>
            <h3 class="font-bold text-sm tracking-wide">Arudhra AI Assistant</h3>
            <p class="text-xs text-blue-100 flex items-center gap-1.5">
              <span class="w-2 h-2 bg-emerald-400 rounded-full"></span> Store RAG Active · Pithapuram
            </p>
          </div>
        </div>
        <button id="rag-chat-close" class="text-white/80 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Quick Suggestion Chips -->
      <div class="bg-slate-50 border-b border-slate-100 px-3 py-2 flex items-center gap-2 overflow-x-auto text-xs no-scrollbar">
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition">📱 Motorola Edge 70</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition">✨ Redmi Note 17 Pro</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition">💻 MacBook Air 2026</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition">🎮 HP Victus 15</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition">🔥 iPhone 18 Pro</button>
      </div>

      <!-- Chat Messages Area -->
      <div id="rag-chat-messages" class="flex-1 p-4 overflow-y-auto space-y-4 text-sm bg-slate-50/50">
        <!-- Initial Bot Greeting -->
        <div class="flex gap-2.5">
          <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold">A</div>
          <div class="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm max-w-[85%] text-slate-800">
            Hello! 👋 I'm your official **Arudhra Mobile Stores** AI Assistant. Ask me about mobile prices, active Instagram poster deals, specs, or availability in Pithapuram!
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <form id="rag-chat-form" class="p-3 bg-white border-t border-slate-100 flex items-center gap-2">
        <input type="text" id="rag-chat-input" placeholder="Ask about phones, prices, posters..." autocomplete="off" class="flex-1 bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition">
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-xl transition shadow-md flex items-center justify-center">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
        </button>
      </form>
    </div>
  `;

  document.body.appendChild(chatContainer);

  const toggleBtn = document.getElementById("rag-chat-toggle");
  const closeBtn = document.getElementById("rag-chat-close");
  const chatWindow = document.getElementById("rag-chat-window");
  const messagesContainer = document.getElementById("rag-chat-messages");
  const chatForm = document.getElementById("rag-chat-form");
  const chatInput = document.getElementById("rag-chat-input");

  toggleBtn.addEventListener("click", () => {
    chatWindow.classList.toggle("hidden");
    if (!chatWindow.classList.contains("hidden")) {
      chatInput.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    chatWindow.classList.add("hidden");
  });

  document.querySelectorAll(".rag-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const text = chip.textContent.replace(/^[^\w]+/, "").trim();
      chatInput.value = text;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Append User Message
    appendMessage("user", query);
    chatInput.value = "";

    // Append Loading Indicator
    const loadingId = appendLoading();

    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query }),
      });

      removeLoading(loadingId);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      appendBotResponse(data);
    } catch (err) {
      removeLoading(loadingId);
      appendMessage(
        "bot",
        "Sorry, I couldn't reach the Arudhra store server. Please check your connection or try again shortly."
      );
    }
  });

  function appendMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `flex gap-2.5 ${sender === "user" ? "justify-end" : ""}`;

    if (sender === "user") {
      msgDiv.innerHTML = `
        <div class="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none max-w-[85%] shadow-sm">
          ${escapeHtml(text)}
        </div>
      `;
    } else {
      msgDiv.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold">A</div>
        <div class="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm max-w-[85%] text-slate-800 space-y-2">
          ${formatMarkdown(text)}
        </div>
      `;
    }

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendBotResponse(data) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "flex gap-2.5";

    let posterCardsHtml = "";
    if (data.products && data.products.length > 0) {
      posterCardsHtml = `
        <div class="mt-3 space-y-3 border-t pt-3 border-slate-100">
          <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Store Poster Offers (Chat RAG):</p>
          <div class="space-y-2">
            ${data.products.map(p => `
              <div class="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-xl p-2.5 text-white flex items-center gap-3 shadow-md border border-indigo-900">
                <img src="${escapeHtml(p.poster_image_path || p.image_path || 'https://via.placeholder.com/150')}" alt="Poster" class="w-16 h-16 object-cover rounded-lg border border-white/20 flex-shrink-0">
                <div class="flex-1 min-w-0">
                  <div class="font-bold text-xs truncate text-amber-300">${escapeHtml(p.name)}</div>
                  <div class="text-[11px] text-slate-200 font-semibold">${p.price ? '₹' + Number(p.price).toLocaleString('en-IN') : 'Deal Price in Store'}</div>
                  <div class="text-[10px] text-slate-400">${escapeHtml(p.ram || '')} ${escapeHtml(p.storage || '')}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold">A</div>
      <div class="bg-white border border-slate-100 p-3.5 rounded-2xl rounded-tl-none shadow-sm max-w-[88%] text-slate-800 space-y-2">
        <div>${formatMarkdown(data.answer || "")}</div>
        ${posterCardsHtml}
      </div>
    `;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendLoading() {
    const id = "loading-" + Date.now();
    const msgDiv = document.createElement("div");
    msgDiv.id = id;
    msgDiv.className = "flex gap-2.5";
    msgDiv.innerHTML = `
      <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-xs font-bold">A</div>
      <div class="bg-white border border-slate-100 p-3 rounded-2xl rounded-tl-none shadow-sm text-slate-500 flex items-center gap-1.5 text-xs">
        <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></span>
        <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:0.2s]"></span>
        <span class="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
        <span>Searching Arudhra store data...</span>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
  }

  function removeLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function formatMarkdown(text) {
    if (!text) return "";
    return escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/• (.*?)(?=\n|$)/g, "• $1<br>")
      .replace(/\n/g, "<br>");
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;",
    }[c]));
  }
})();
