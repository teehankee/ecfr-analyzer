import { useState } from "react";
import React from "react";
export default function ReloadButton({ initialTs, onDone }) {
  const [busy, setBusy] = useState(false);

  const pollUntilNew = async () => {
    while (true) {
      await new Promise((res) => setTimeout(res, 2000)); // 2‑sec poll
      const m = await fetch("/api/metrics").then((r) => r.json());
      if (m.generated && m.generated !== initialTs) return;
    }
  };

  const handleClick = async () => {
    setBusy(true);
    try {
      const r = await fetch("/api/reload", { method: "POST" });
      if (!r.ok) throw new Error(`Reload failed (${r.status})`);
      await pollUntilNew();  // wait here until metrics timestamp changes
      await onDone();        // refresh UI
    } catch (e) {
      console.error(e);
      alert(e.message || "Reload failed – check server log.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={busy}
      className={`px-4 py-1 rounded text-white ${
        busy ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
      }`}
    >
      {busy ? "Regenerating…" : "Regenerate Data"}
    </button>
  );
}
