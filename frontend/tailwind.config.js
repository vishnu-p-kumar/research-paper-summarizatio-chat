/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "Inter", "sans-serif"]
      },
      colors: {
        fz: {
          base: "var(--color-base)",
          panel: "var(--color-panel)",
          border: "var(--color-border)",
          primary: "var(--color-primary)",
          secondary: "var(--color-secondary)",
          accent: "var(--color-accent)",
          text: "var(--color-text)",
          textmuted: "var(--color-text-muted)"
        }
      },
      boxShadow: {
        glass: "0 4px 30px rgba(0, 0, 0, 0.1)",
        glow: "0 0 20px var(--color-primary-glow)"
      }
    }
  },
  plugins: []
};

