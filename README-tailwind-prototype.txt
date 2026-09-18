Arudhra Tailwind Prototype

Files:
- index-tailwind.html  — Home / Hero / Featured products
- shop-tailwind.html   — Product listing with sidebar filters
- product-tailwind.html — Product detail page
- cart-tailwind.html   — Cart summary
- checkout-tailwind.html — Checkout & shipping

How to preview:
1. Open any of the HTML files in a browser (double-click or right-click -> Open with).
2. These pages use Tailwind Play CDN (https://cdn.tailwindcss.com) so no build step is required.

Notes & next steps:
- This is a front-end prototype using Tailwind CDN for quick preview. For production,
  switch to a PostCSS/Tailwind build and purge unused styles.
- Replace placeholder images with real assets in an /assets/ folder.
- If desired, the header/footer can be converted into includes or React components.

If you'd like, next actions can be:
- Convert these templates into a Vite + React app with Tailwind CLI (build flow)
- Extract header/footer into include partials
- Provide a responsive spec and asset export list
- Implement minimal JS for cart interactions (add/remove items)

(I'm an AI assistant using Copilot CLI runtime in VS Code.)