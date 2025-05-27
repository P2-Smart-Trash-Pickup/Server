import { defineConfig } from "vite";
import dns from "node:dns";

dns.setDefaultResultOrder("verbatim");

export default defineConfig({
  server: {
    allowedHosts: ["emission-occupation-ranger-roster.trycloudflare.com"],
  },
});
