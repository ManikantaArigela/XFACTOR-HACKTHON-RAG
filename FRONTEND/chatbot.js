(() => {
  const apiBase = window.ARUDHRA_API_BASE_URL || "http://127.0.0.1:5000/api";

  // Conversation history for multi-turn conversational AI
  let chatHistory = [];

  // Create Chatbot UI HTML Container
  const chatContainer = document.createElement("div");
  chatContainer.id = "arudhra-rag-chatbot-root";
  chatContainer.className = "fixed bottom-5 right-5 z-50 font-sans";

  chatContainer.innerHTML = `
    <!-- Floating Chat Trigger Button -->
    <button id="rag-chat-toggle" class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold px-4 py-3 rounded-full shadow-2xl flex items-center gap-2.5 transition-all transform hover:scale-105 active:scale-95">
      <div class="relative flex items-center justify-center">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
        <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full animate-ping"></span>
        <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full"></span>
      </div>
      <span>Ask Store AI</span>
    </button>

    <!-- Chat Modal Window -->
    <div id="rag-chat-window" class="hidden fixed bottom-20 right-5 w-96 max-w-[calc(100vw-2.5rem)] h-[560px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden transition-all duration-300">
      
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-600 text-white p-3.5 flex items-center justify-between shadow-sm">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-base">🤖</div>
          <div>
            <h3 class="font-bold text-xs tracking-wide">Arudhra AI Assistant</h3>
            <p class="text-[11px] text-blue-100 flex items-center gap-1">
              <span class="w-2 h-2 bg-emerald-400 rounded-full inline-block"></span> Local Store RAG · Pithapuram
            </p>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <button id="rag-chat-clear" title="Clear conversation" class="text-white/80 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button>
          <button id="rag-chat-close" title="Close" class="text-white/80 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>

      <!-- Quick Suggestion Chips -->
      <div class="bg-slate-50 border-b border-slate-100 px-3 py-2 flex items-center gap-1.5 overflow-x-auto text-xs no-scrollbar">
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition shadow-2xs">🔥 Apple 18 Pro</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition shadow-2xs">📱 Price of iPhone 15?</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition shadow-2xs">⚡ OnePlus Nord CE4 Fast Charging?</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition shadow-2xs">💰 5G under ₹30,000</button>
        <button class="rag-chip bg-white border border-slate-200 text-slate-700 px-2.5 py-1 rounded-full whitespace-nowrap hover:border-blue-500 hover:text-blue-600 transition shadow-2xs">📍 Store Location</button>
      </div>

      <!-- Chat Messages Area -->
      <div id="rag-chat-messages" class="flex-1 p-3.5 overflow-y-auto space-y-3.5 text-xs bg-slate-50/40">
        <!-- Initial Bot Greeting -->
        <div class="flex gap-2">
          <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold">A</div>
          <div class="bg-white border border-slate-200/80 p-3 rounded-2xl rounded-tl-none shadow-xs max-w-[88%] text-slate-800" id="rag-initial-greeting">
            Hello! 👋 I'm your official **Arudhra Mobile Stores** AI Assistant. Ask me about specific phone prices, fast charging, specs, or availability in Pithapuram!
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <form id="rag-chat-form" class="p-2.5 bg-white border-t border-slate-100 flex items-center gap-2">
        <input type="text" id="rag-chat-input" placeholder="Ask about price, specs, fast charging..." autocomplete="off" class="flex-1 bg-slate-100/80 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition">
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-xl transition shadow-xs flex items-center justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
        </button>
      </form>
    </div>
  `;

  document.body.appendChild(chatContainer);

  const toggleBtn = document.getElementById("rag-chat-toggle");
  const closeBtn = document.getElementById("rag-chat-close");
  const clearBtn = document.getElementById("rag-chat-clear");
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

  clearBtn.addEventListener("click", () => {
    chatHistory = [];
    messagesContainer.innerHTML = `
      <div class="flex gap-2">
        <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold">A</div>
        <div class="bg-white border border-slate-200/80 p-3 rounded-2xl rounded-tl-none shadow-xs max-w-[88%] text-slate-800">
          Chat reset! 👋 Ask me anything about our phone models, live prices, or store in Pithapuram.
        </div>
      </div>
    `;
    updateBotGreeting();
  });

  function updateBotGreeting() {
    const greetingEl = document.getElementById("rag-initial-greeting");
    if (!greetingEl) return;
    const user = window.ArudhraAuth ? window.ArudhraAuth.getUser() : null;
    if (user) {
      greetingEl.innerHTML = `Hello <strong>${escapeHtml(user.full_name || user.email)}</strong>! 👋 I'm your official <strong>Arudhra Mobile Stores</strong> AI Assistant. Ask me about specific phone prices, fast charging, specs, or availability in Pithapuram!`;
    }
  }
  updateBotGreeting();
  window.addEventListener("arudhra:auth-changed", updateBotGreeting);

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

    // Append User Message to UI
    appendMessage("user", query);
    chatInput.value = "";

    // Append Loading Indicator
    const loadingId = appendLoading();

    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          history: chatHistory.slice(-8) // Send up to last 8 turns for context
        }),
      });

      removeLoading(loadingId);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      
      // Update local conversational history
      chatHistory.push({ role: "user", content: query });
      chatHistory.push({ role: "assistant", content: data.answer || "" });

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
    msgDiv.className = `flex gap-2 ${sender === "user" ? "justify-end" : ""}`;

    if (sender === "user") {
      msgDiv.innerHTML = `
        <div class="bg-blue-600 text-white px-3 py-2 rounded-2xl rounded-tr-none max-w-[85%] shadow-xs leading-relaxed">
          ${escapeHtml(text)}
        </div>
      `;
    } else {
      msgDiv.innerHTML = `
        <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold">A</div>
        <div class="bg-white border border-slate-200/80 px-3 py-2.5 rounded-2xl rounded-tl-none shadow-xs max-w-[88%] text-slate-800 leading-relaxed space-y-1.5">
          ${formatMarkdown(text)}
        </div>
      `;
    }

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendBotResponse(data) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "flex gap-2";

    // Sleek, compact product cards
    let productsHtml = "";
    if (data.products && data.products.length > 0) {
      productsHtml = `
        <div class="mt-2.5 pt-2 border-t border-slate-100 space-y-1.5">
          <p class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Relevant Inventory:</p>
          <div class="grid grid-cols-1 gap-1.5">
            ${data.products.map(p => `
              <div class="bg-slate-50 border border-slate-200/70 hover:border-blue-400 rounded-xl p-2 flex items-center justify-between gap-2 transition group">
                <div class="min-w-0 flex-1">
                  <div class="font-bold text-xs text-slate-900 truncate group-hover:text-blue-600 transition">${escapeHtml(p.name)}</div>
                  <div class="text-[11px] font-semibold text-blue-700">
                    ${p.price ? '₹' + Number(p.price).toLocaleString('en-IN') : 'Store Offer'}
                    ${p.ram || p.storage ? `<span class="text-slate-400 font-normal ml-1">(${escapeHtml(p.ram || '')}${p.ram && p.storage ? ' · ' : ''}${escapeHtml(p.storage || '')})</span>` : ''}
                  </div>
                </div>
                <a href="shop-tailwind.html?search=${encodeURIComponent(p.name)}" class="bg-blue-50 hover:bg-blue-600 text-blue-600 hover:text-white px-2 py-1 rounded-lg text-[10px] font-medium transition flex-shrink-0">
                  Shop
                </a>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold">A</div>
      <div class="bg-white border border-slate-200/80 px-3 py-2.5 rounded-2xl rounded-tl-none shadow-xs max-w-[88%] text-slate-800 leading-relaxed">
        <div class="space-y-1">${formatMarkdown(data.answer || "")}</div>
        ${productsHtml}
      </div>
    `;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendLoading() {
    const id = "loading-" + Date.now();
    const msgDiv = document.createElement("div");
    msgDiv.id = id;
    msgDiv.className = "flex gap-2";
    msgDiv.innerHTML = `
      <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex-shrink-0 flex items-center justify-center text-[10px] font-bold">A</div>
      <div class="bg-white border border-slate-200/80 px-3 py-2 rounded-2xl rounded-tl-none shadow-xs text-slate-500 flex items-center gap-1.5 text-xs">
        <span class="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce"></span>
        <span class="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce [animation-delay:0.2s]"></span>
        <span class="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
        <span class="text-[11px] text-slate-500">Checking Arudhra store RAG...</span>
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
