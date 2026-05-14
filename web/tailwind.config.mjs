/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "system-ui", "ui-sans-serif", "sans-serif"],
        serif: ['"Lora"', "ui-serif", "Georgia", "serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        ink: {
          50: "#f7f7f6",
          100: "#e7e6e2",
          200: "#cfcdc6",
          300: "#a8a59c",
          400: "#79766d",
          500: "#534f47",
          600: "#3a3731",
          700: "#27241f",
          800: "#1a1814",
          900: "#100e0b",
        },
        gold: {
          50: "#fdf8ed",
          100: "#f9ecc8",
          200: "#f3d588",
          300: "#ecbb4e",
          400: "#dba023",
          500: "#b58018",
          600: "#8f6212",
          700: "#6b4710",
          800: "#4a300c",
          900: "#2f1e07",
        },
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.ink.700"),
            "--tw-prose-headings": theme("colors.ink.900"),
            "--tw-prose-links": theme("colors.gold.600"),
            "--tw-prose-code": theme("colors.ink.700"),
            maxWidth: "70ch",
          },
        },
        invert: {
          css: {
            "--tw-prose-body": theme("colors.ink.200"),
            "--tw-prose-headings": theme("colors.ink.50"),
            "--tw-prose-links": theme("colors.gold.300"),
            "--tw-prose-code": theme("colors.ink.200"),
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
